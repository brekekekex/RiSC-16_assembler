	lw	1,0,count	# load reg1 with 5 (uses symbolic address)
	lw	2,1,2	# load reg2 with -1 (uses numeric address)
start:	add	1,1,2	# decrement reg1
	bne	0,1,start	# go back to the beginning of the loop unless reg1==0
done:	halt
	nop
count:	.fill	5
neg1:	.fill	-1
startAddr:	.fill	start	# will contain the address of start (2)