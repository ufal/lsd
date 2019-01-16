#!/usr/bin/python3

sentence = "President Bush on Tuesday nominated two individuals to replace retiring jurists on federal courts in the Washington area ."
tokens = sentence.split(' ')

print('#sentence: ' + sentence) 
c = 0        
for i in range(len(tokens)):
    print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
    c += 1
print()

for k in range(len(tokens)):
    for l in range(len(tokens) - k - 1):
        print('#skipped: ' + " ".join(str(x) for x in range(k, k + l + 1))) 
        c = 0
        for i in range(len(tokens)):
            if i < k or i > k + l:
                print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
                c += 1
        print()


