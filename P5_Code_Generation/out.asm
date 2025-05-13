	LW $s0, n
L2:
	BLT i, 2, L32
	LI $s1, 1
	LI $s2, 2
L5:
	BGT j, 1, L16
	LW $t0, j
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	LW $s3, x
	LW $t1, x
	ADD, $t1, $t1, $t0
	LW $t0, jmax
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	LW $t2, x
	ADD, $t2, $t2, $t0
	BLE T3, T6, L14
L14:
	MOVE $s1, $s2
	ADDI, $s1, $s1, 1
	JAL L5
L16:
	BEQ jmax, i, L30
	LW $t0, i
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	LW $t3, x
	ADD, $t3, $t3, $t0
	LW $t0, jmax
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	LW $t4, x
	ADD, $t4, $t4, $t0
	LW $t0, i
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	MOVE $t5, $s3
	ADD, $t5, $t5, $t0
	SW $t5, (x[T14])
	LW $t0, jmax
	SUBI, $t0, $t0, 1
	MULTI, $t0, $t0, 4
	MOVE $t5, $s3
	ADD, $t5, $t5, $t0
	SW $t5, (x[T16])
L30:
	MOVE $s4, $s0
	SUBI, $s4, $s4, 1
	JAL L2
L32:
	JR $ra
	SW $s0, (n)
	SW $s1, (j)
	SW $s2, (jmax)
	SW $s3, (x)
	SW $s4, (i)
