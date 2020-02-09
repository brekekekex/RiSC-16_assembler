lw 1, 0, count
lw 2, 1, 2
start: add 1,1,2 
beq 0,1,1
beq 0, 0, start
done: halt
count: .fill 5
neg1: .fill -1
startAddr: .fill start
