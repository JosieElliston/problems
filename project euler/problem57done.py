num = 1
den = 1
counter = 0
for i in range(1000):
	num, den = num + 2*den, den + num
	if len(str(num)) > len(str(den)): counter += 1
print(counter)