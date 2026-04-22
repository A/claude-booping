## Project Resolution Principle

- Check if there is a file `.booping`.
- If the file doesn't exist, tell the user to select a project, and ask if they want to persist the project by creating a `.booping` file.
- If the file is created, ask the user if they want to gitignore it.
- Make a new file `.booping` and put `project_name: {project_name}` in it.
- `project_name` is the project name.

New project name should be kebab-cased and based on the project directory name or on the parent and project directory names, depends on how clear is it.
When creating new project, ask user to confirm name or give its own name
