#vigilant-tribble
On the terminal execute the below command to create the projects' working directory and move into that directory.

 
```python
$ mkdir vigilant-tribble
cd vigilant-tribble
```

In the projects' working directory execute the below command to create a virtual environment for our project. Virtual environments make it easier to manage packages for various projects separately.

 
```python
$ py -m venv venv
```

To activate the virtual environment, execute the below command.

```python
$ source venv/Scripts/activate
```
Clone this repository in the projects' working directory by executing the command below.

```python
$ git clone https://github.com/ajaoooluseyi/vigilant-tribble.git
$ cd crispy-spoon
```

To install all the required dependencies execute the below command.

```python
$ pip install -r requirements.txt
```

To run the app, navigate to the app folder in your virtual environment and execute the command below
```python
$ uvicorn main:app --reload
```
