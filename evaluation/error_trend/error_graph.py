import matplotlib.pyplot as plt

with open("log3.txt",'r') as f:
	lines = f.readlines()

epoch, error = list(), list()
for line in lines:
	if line.startswith("Epoch "):
		val = line.split()
		epoch.append(float(val[1]))
		error.append(float(val[5]))

plt.xlabel("Epoch")
plt.ylabel("Error")
plt.plot(epoch, error)
plt.show()