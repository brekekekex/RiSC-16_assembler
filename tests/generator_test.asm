# Taken from classweb.ece.umd.edu/enee646.F2011/p1.pdf
	lw 1, 0, count	# load reg1 with 5 (uses symbolic address)
	lw 2, 1, 2	# load reg2 with -1 (uses numeric address)
start: 	add 1, 1, 2 	# decrement reg1 (could have been 'addi 1, 1, -1')
	beq 0, 1, start	# changed from bne to beq 
done: 	halt
	nop
count: 	.fill 5
neg1: 	.fill -1
startAddr: .fill start
