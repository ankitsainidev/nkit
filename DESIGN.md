# Nkit
## Code
```
@app.command()
def some_command():
	# This part is only for formatting the data, nothing else
	# everything goes into other functions/classes
```
## File structure
```
main.py # command execution

tools/
	__init__.py # make enum and take them all together
	notes.py
	keys.py
	..

storage/
	local.py
	remote.py 
```
