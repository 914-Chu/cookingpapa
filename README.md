# CS411-cookingpapa

<p>Hello daddies! Welcome to CookingPapa with Joyce, Ardel, Nina, and Kamil; A.K.A JANK. If you want to run this application locally we are using VS Code so follow these steps:</p>

## Prerequisites
<ol>
  <li> Installed VS Code (macOS/Windows)
  <li> Installed <a href="https://marketplace.visualstudio.com/items?itemName=ms-python.python"> Python extension </a>
  <li> Installed a version of Python 3
</ol>

## Setting Up
### Environment
<p>Clone the project into your favorite directory.<br><br>
Create a virtual environment based on your current interpreter<br>

```
  # macOS/Linux
  sudo apt-get install python3-venv    # If needed
  python3 -m venv venv

  # Windows
  python -m venv venv
```

Open the project in VS Code<br><br>
To activate the virtual environment (venv), in VS Code, open the Command Palette (<b>View > Command Palette</b>). Then select the <b>Python: Select Interpreter command:</b><br><br>
From the list, select the virtual environment in your project folder that starts with <b>./env</b> or <b>.\env</b> <br><br>
To create a terminal and automatically activate the virtual environment chosen, run <b>Terminal: Create New Integrated Terminal</b></p>
<ul><li><p>alternatively, in your VS Code terminal type the following: <b><em>source venv/bin/activate</em></b></p></li></ul>
<p><i>NOTE: Ensure that your current user in the terminal is prefixed with <b>(venv)</b> </i></p>

### Installing dependencies
<p>We provide a <em>requirements.txt</em> file that you can run to obtain all dependencies required to run the application. Simply run

```
  pip3 install -r requirements.txt
```
</p>

## Running the application
<p>After completing the above steps we can now run the application locally, run the following in the terminal

For macOS/Linux:

```
  python3 install flask -run
```
For Windows:

```
  python install flask -run
```

Now, open your default browser and go to the our landing page <em>http://127.0.0.1:5000/index</em>
</p>

## Notes
<p>Everytime you fetch and pull, you <em><b>probably</b></em> will need to delete your virtual environment folder <b>venv/</b> and redo these steps. Sorry!</p>
<p>If things go south, visit <em>https://code.visualstudio.com/docs/python/tutorial-flask</em></p>
