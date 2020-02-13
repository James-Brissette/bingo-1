class stackGenerator():

        def __init__(self):
                self.terminalStack = []
                self.constantStack = []
                self.stack = []
                self.operatorList = ['+','-','*','/','sin','cos','exp','log','^','abs','sqrt']

        def _getSubFunction(self, func):
                subFunc = ''
                parenCt = 1
                i = 0
                while parenCt > 0:
                        parenCt = parenCt + (func[i]=='(')
                        parenCt = parenCt - (func[i]==')')
                        subFunc = subFunc + func[i]
                        i = i + 1
                return str(subFunc[:-1])

        def _commandLookup(self, operator):
                return self.operatorList.index(operator) + 2 

        def generateDAG(self, func):
                command = [None, None, None]
                token = ''
                i = 0
                local = False #local means command needs to reference an index in the global stack
                pendingToken = False
                endsWithVar = False

                while i < len(func):
                        endsWithVar = False
                        if (func[i] == '('):
                                i = i + 1
                                subFunc = self._getSubFunction(func[i:])
                                self.generateDAG(subFunc)
                                if pendingToken and len(self.terminalStack):
                                        if isinstance(self.terminalStack[-1],str):
                                                try:
                                                    self.stack.append([1, self.constantStack.index(float(self.terminalStack[-1])),0])
                                                except:
                                                    self.constantStack.append(float(self.terminalStack[-1]))
                                                    self.stack.append([1,len(self.constantStack)-1,0])
                                                    
                                                command[2] = len(self.stack)-1
                                        else:
                                                command[2] = self.terminalStack[-1]
                                        self.terminalStack = self.terminalStack[:-1]
                                        self.stack.append([self._commandLookup(command[0]),command[1],command[2]])
                                        pendingToken = False
                                        local = True
                                elif len(self.terminalStack):
                                        token = self.terminalStack[0]
                                        self.terminalStack = self.terminalStack[:-1]
#                                else:
#                                        self.terminalStack.append(len(self.stack) - 1)

                                local = True
                                i = i + len(subFunc)

                        elif (func[i] in ['c','s','e','z','I','?']): #cos,sin,exp,scientific notation,zoo
                                if (func[i] == 'e' and func[i+1] != 'x'):
                                    token = token + func[i:i+2]
                                    i = i + 1
                                elif (func[i] == 'z'):
                                    i = i + 2
                                    token = '1'
                                elif (func[i] in ['I','?']):
                                    token = '1'
                                else:
                                    j = i + 4
                                    subFunc = self._getSubFunction(func[j:])
                                    self.generateDAG(subFunc)
                                    local = True
                                    if len(self.terminalStack):
                                            if isinstance(self.terminalStack[-1],str):
                                                    try:
                                                        self.stack.append([1, self.constantStack.index(float(self.terminalStack[-1])),0])
                                                    except:
                                                        self.constantStack.append(float(self.terminalStack[-1]))
                                                        self.stack.append([1,len(self.constantStack)-1,0])
                                                    self.stack.append([self._commandLookup(func[i:j-1]),len(self.stack)-1,0])
                                            else:
                                                    self.stack.append([self._commandLookup(func[i:j-1]),self.terminalStack[-1],0])
    
                                            self.terminalStack = self.terminalStack[:-1]
                                    else:
                                            self.stack.append([self._commandLookup(func[i:j-1]),len(self.stack) - 1,0])
    
                                    i = j + len(subFunc)
                                    pendingToken = True

                        elif (func[i] in ['+','-','*','/','^']):
                                if pendingToken and not command[0]==None:
                                        if token == '':
                                            command[2] = len(self.stack) - 1
                                        else:
                                            try:
                                                f=float(token)
                                                self.constantStack.append(f)
                                                self.stack.append([1, len(self.constantStack)-1, 0])
                                                
                                                try:
                                                    self.stack.append([1, self.constantStack.index(f),0])
                                                except:
                                                    self.constantStack.append(f)
                                                    self.stack.append([1,len(self.constantStack)-1,0])
                                                
                                                command[2] = len(self.stack)-1
                                            except:
                                                command[2] = token
                                                
                                        self.stack.append([self._commandLookup(command[0]),command[1],command[2]])
                                        local = True
                                        command[0] = func[i]
                                        command[1] = len(self.stack) - 1
                                        token = ''
                                #Handles Negative variables and constants
                                elif (not pendingToken and func[i] == '-'):
                                    try:
                                        self.stack.append([1, self.constantStack.index(float(-1)),0])
                                    except:
                                        self.constantStack.append(float(-1))
                                        self.stack.append([1,len(self.constantStack)-1,0])
                                    
                                    command[0] = '*'
                                    command[1] = len(self.stack)-1
                                    pendingToken = True
                                    
                                else:
                                    command[0] = func[i]
                                    if (local):
                                        #command[1] = len(self.stack) - 1
                                        if not token == '':
                                            command[1] = token
                                        else:
                                            command[1] = len(self.stack) - 1
                                    else:
                                        if isinstance(token,str):
                                            try:
                                                token = self.constantStack.index(float(token))
                                                try:
                                                    command[1] = self.stack.index([1,token,0])
                                                except:
                                                    self.stack.append([1,len(self.constantStack)-1,0])
                                                    command[1] = len(self.stack)-1 
                                            except:
                                                self.constantStack.append(float(token))
                                                self.stack.append([1,len(self.constantStack)-1,0])
                                                command[1] = len(self.stack)-1
                                                
                                        else:
                                            command[1] = token
                                    token = ''
                                    pendingToken = True

                        # Variables X_0 through X_n go into their own buffers
                        # example: [0,n,n]
                        elif (func[i] in ['X','x']):
                                i = i + 2
                                try:
                                    token = self.stack.index([0,int(func[i]),int(func[i])])
                                except:
                                    self.stack.append([0,int(func[i]),int(func[i])])
                                    token = len(self.stack) - 1
                                endsWithVar = True

                        else:
                                if (not func[i].isspace()):
                                        token = str(token) + str(func[i])
                                        pendingToken = True

                        i = i + 1


                if (command[1] == None):
                        if (not token == ''):
                                if (isinstance(token,str)):
                                    f=float(token)
                                    
                                    try:
                                        #self.stack.append([1, self.constantStack.index(f), 0])
                                        token = self.constantStack.index(f)
                                    except:
                                        self.constantStack.append(f)
                                        self.stack.append([1, len(self.constantStack)-1, 0])
                                        token = len(self.stack)-1
                                    self.terminalStack.append(token)
                                else:
                                    self.terminalStack.append(token)
                else:
                        if (pendingToken):
                                if (token == ''):
                                        command[2] = len(self.stack) - 1
                                elif (endsWithVar):
                                    command[2] = token
                                else:
                                    try:
                                        f=float(token)
                                        try:
                                            self.stack.append([1, self.constantStack.index(f), 0])
                                        except:
                                            self.constantStack.append(f)
                                            self.stack.append([1, len(self.constantStack)-1, 0])
                                        command[2] = len(self.stack)-1
                                    except:
                                        command[2] = token

                                self.stack.append([self._commandLookup(command[0]),command[1],command[2]])
                                
                

                return
          
        def distributeArray(self,commandStack, newStack):
                ct = len(newStack)
                if (ct == 0):
                        print("Command Stack: ",commandStack)
                        print("NewStack: ", newStack)
                k = int(len(commandStack) / ct)
                for i in range(len(newStack[:-1])):
                        idx = i*k
                        commandStack[idx] = newStack[i]
                        if commandStack[idx][0] > 1:
                                commandStack[idx] = [commandStack[idx][0], commandStack[idx][1] * k, commandStack[idx][2] * k]

                commandStack[-1] = newStack[-1]
                if commandStack[-1][0] > 1:
                        commandStack[-1] = [commandStack[-1][0], commandStack[-1][1] * k, commandStack[-1][2] * k]

                return commandStack
        
    
            
        
    
            
            
    
generator = stackGenerator()
#func = '(-X_0 + cos(X_0))^(2*X_0)*cos(X_0)^75659.26967056174'
func = '(2 - (2))^(2 - (2)) + (2 - (2))^(2 - (2))'
generator.generateDAG(func)
print('func: ',func)
print("stack: ",generator.stack)
print("constantStack: ",generator.constantStack)
print("terminalStack: ",generator.terminalStack)


"""================ Simplification Test ================
        print("Command Stack:")
        print(self._command_array)
        print("Constant Stack:")
        print(self._simplified_constants)
        console_string = get_formatted_string("console", self._simplified_command_array, self._simplified_constants)        
        print("Console String: ", console_string)
        print("Latex String: ", self.get_latex_string())

        print("")
        generator = stackGenerator()
        generator.generateDAG(console_string)
        print("Generated Stack:")
        print(generator.stack)
        print("Generated Constants:")
        print(generator.constantStack)
        print("")

        print("Distributing Generated Stack into Command Stack:")
        self._command_array = generator.distributeArray(self._command_array,generator.stack)
        self._simplified_constants = generator.constantStack
        print(self._command_array)

        #print("Sympy String: ", self.get_sympy_string())

        input("")"""
