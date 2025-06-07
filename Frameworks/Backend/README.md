# Gin, Fiber, Echo

## Basics of Go

After running below commands, your Go project should be initialized, committed to Git, and pushed to your GitHub repository.

Here's how to initialize a new Go project and commit it to a GitHub repository using the go init command:

1. Create a new directory:

        
	$ mkdir <project_name>

	$ cd <project_name>

2. Initialize a Go module:

	$ go mod init <project_name>

Replace <project_name> with your desired project name (e.g., my-go-app).

The go command creates go.mod file which tracks the project's dependencies.

3. Create your Go files:

Create your main.go file, or any other Go files you need.

4. Initialize a Git repository:

	$ git init

The git init command initializes a new Git repository in your project's root directory.

5. Add your files:

	$ git add .

The git add . command stages all files in your project for commit. You can also use git add <file_name> to add individual files. 

6. Commit your changes:

	$ git commit -m "Initial commit"

The git commit command commits your staged changes with the message "Initial commit".

7. Create a new repository on GitHub:

Go to GitHub and create a new repository with the same name as your project (<project_name>).

8. Add the remote repository:

	$ git remote add origin <repository_url>

Replace <repository_url> with the URL you copied from GitHub.

9. Rename the branch to main.

	$ git branch -M main

8. Push the changes to GitHub.

	$ git push -u origin main

The git push command pushes your local commits to the remote repository on GitHub. 

## References

How to write Go code

https://go.dev/doc/code
