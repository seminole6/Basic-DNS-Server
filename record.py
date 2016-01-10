import pickle 

class record:

	def __init__(self,name,value):
		self.name=name
		self.value=value


#example of how to save objects using pickle

#a = record("a","b","c")

#b = record("d","e","f")

#record_holder = []

#record_holder.append(a);
#record_holder.append(b);

#f= open('database.pkl','w+')
#pickle.dump(record_holder,f)
#f.close()

#f=open('database.pkl','r+') 
#newlist = pickle.load(f)
#f.close()

#for item in record_holder:
	#print item.name

