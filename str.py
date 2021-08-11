
Stack = []
while True:
    x = int(input("Enter an int vaue (<0 to end) :"))
    if x < 0:
        break
    Stack.append(x)
    print(f'Stack size = {len(Stack)} Stack data = {Stack}')
    
for i in range(len(Stack)):
    print(f'Stack of pop = {Stack.pop()}')
