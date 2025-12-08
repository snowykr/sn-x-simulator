import re

class SNXSimulator:
    def __init__(self, code_str):
        self.regs = [0] * 4  # $0 ~ $3
        self.memory = [0] * 128  # 128 워드 메모리
        self.pc = 0
        self.instructions = []
        self.labels = {}
        self.running = True

        # 코드 파싱
        self._parse_code(code_str)

    def _parse_code(self, code_str):
        lines = code_str.strip().split('\n')
        actual_line_idx = 0

        # 1. 라벨과 명령어 분리
        for line in lines:
            line = line.split(';')[0].strip()  # 주석 제거
            if not line: continue

            # 라벨 처리 (예: "foo:")
            if ':' in line:
                label_part, code_part = line.split(':', 1)
                self.labels[label_part.strip()] = actual_line_idx
                line = code_part.strip()

            if not line: continue

            # 명령어 파싱 (공백, 콤마로 분리)
            parts = re.split(r'[,\s]+', line)
            opcode = parts[0].upper()
            operands = parts[1:]

            self.instructions.append({'opcode': opcode, 'operands': operands, 'raw': line})
            actual_line_idx += 1

    def _get_reg_idx(self, reg_str):
        # "$1" -> 1 변환
        return int(reg_str.replace('$', ''))

    def _calc_effective_addr(self, addr_str):
        # "offset($reg)" 형식 파싱
        match = re.match(r'(-?\d+)\((\$\d)\)', addr_str)
        if match:
            offset = int(match.group(1))
            reg_idx = self._get_reg_idx(match.group(2))

            # EA <- I + (Rb == $0)? 0 : Rb
            # $0은 주소 계산 시 0으로 취급
            base_val = 0 if reg_idx == 0 else self.regs[reg_idx]
            return offset + base_val
        return 0

    def step(self):
        if not self.running or self.pc >= len(self.instructions):
            self.running = False
            return

        inst = self.instructions[self.pc]
        op = inst['opcode']
        args = inst['operands']

        # 현재 상태 출력용 저장
        current_pc = self.pc
        current_inst = inst['raw']

        # PC 증가
        self.pc += 1

        # --- 명령어 작동 정의 ---
        if op == 'LDA':
            dest = self._get_reg_idx(args[0])
            addr = self._calc_effective_addr(args[1])
            self.regs[dest] = addr

        elif op == 'LD':
            dest = self._get_reg_idx(args[0])
            addr = self._calc_effective_addr(args[1])
            self.regs[dest] = self.memory[addr]

        elif op == 'ST':
            src = self._get_reg_idx(args[0])
            addr = self._calc_effective_addr(args[1])
            self.memory[addr] = self.regs[src]

        elif op == 'ADD':
            dest = self._get_reg_idx(args[0])
            val1 = self.regs[self._get_reg_idx(args[1])]
            val2 = self.regs[self._get_reg_idx(args[2])]
            self.regs[dest] = val1 + val2

        elif op == 'SLT':
            dest = self._get_reg_idx(args[0])
            val1 = self.regs[self._get_reg_idx(args[1])]
            val2 = self.regs[self._get_reg_idx(args[2])]
            self.regs[dest] = 1 if val1 < val2 else 0

        elif op == 'BZ':
            cond_reg = self._get_reg_idx(args[0])
            label = args[1]
            if self.regs[cond_reg] == 0:
                self.pc = self.labels[label]

        elif op == 'BAL':
            link_reg = self._get_reg_idx(args[0])
            next_pc = self.pc  # 이미 증가된 PC (복귀 주소)

            # 타겟 주소 계산
            target_pc = 0
            if args[1] in self.labels:
                target_pc = self.labels[args[1]]
            else:
                target_pc = self._calc_effective_addr(args[1])

            # 레지스터 업데이트 및 점프
            self.regs[link_reg] = next_pc
            self.pc = target_pc

        elif op == 'HLT':
            self.running = False

        # --- Trace Table 출력 ---
        print(
            f"| {current_pc:<3} | {current_inst:<15} | {self.regs[0]:<3} | {self.regs[1]:<3} | {self.regs[2]:<3} | {self.regs[3]:<3} |")


# --- 실행 데이터  ---
asm_code = """
main:
    LDA $3, 64($0)
    LDA $1, 3($0)
    BAL $2, foo
    HLT

foo:
    LDA $3, -2($3)
    ST  $2, 0($3)
    ST  $1, 1($3)
    LDA $0, 2($0)
    SLT $0, $1, $0
    BZ  $0, foo2
foo1:
    LD  $2, 0($3)
    LDA $3, 2($3)
    BAL $2, 0($2)
foo2:
    LDA $1, -1($1)
    BAL $2, foo
    LDA $3, -1($3)
    ST  $1, 0($3)
    LD  $1, 2($3)
    LDA $1, -2($1)
    BAL $2, foo
    LD  $2, 0($3)
    LDA $3, 1($3)
    ADD $1, $1, $2
    BAL $0, foo1
"""

# 시뮬레이터 실행
sim = SNXSimulator(asm_code)

print(f"| PC  | OPREG           | $0  | $1  | $2  | $3  |")
print(f"| --- | --------------- | --- | --- | --- | --- |")

while sim.running:
    sim.step()