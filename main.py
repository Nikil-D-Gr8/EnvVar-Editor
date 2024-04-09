import os
import tkinter as tk
from tkinter import messagebox
import winreg

class EnvironmentVariableEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Environment Variable Editor")
        self.root.geometry("500x300")  

        self.create_widgets()

    def create_widgets(self):
        center_frame = tk.Frame(self.root)
        center_frame.pack(expand=True)

        var_name_label = tk.Label(center_frame, text="Variable Name:")
        var_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.var_name_entry = tk.Entry(center_frame)
        self.var_name_entry.grid(row=0, column=1, padx=5, pady=5)

        var_value_label = tk.Label(center_frame, text="Variable Value:")
        var_value_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.var_value_entry = tk.Entry(center_frame)
        self.var_value_entry.grid(row=1, column=1, padx=5, pady=5)

        set_button = tk.Button(center_frame, text="Set Variable", command=self.set_environment_variable)
        set_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        clear_button = tk.Button(center_frame, text="Clear Entries", command=self.clear_entries)
        clear_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        self.var_frame = tk.Frame(center_frame)
        self.var_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        self.populate_listbox()

        delete_button = tk.Button(center_frame, text="Delete Selected", command=self.delete_selected)
        delete_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="we")

    def populate_listbox(self):
        self.checkboxes = {}
        for var_name, var_value in os.environ.items():
            if self.is_user_defined(var_name):
                # Format the checkbox text with line breaks if the variable name is too long
                checkbox_text = self.wrap_text(var_name, var_value)
                var_checkbox = tk.Checkbutton(self.var_frame, text=checkbox_text)
                var_checkbox.pack(anchor="w")
                self.checkboxes[var_name] = var_checkbox

    def wrap_text(self, var_name, var_value):
        max_width = 40  # Maximum width for the variable name
        if len(var_name) > max_width:
            wrapped_text = [var_name[i:i+max_width] for i in range(0, len(var_name), max_width)]
            return '\n'.join(wrapped_text) + f"={var_value}"
        else:
            return f"{var_name}={var_value}"



    def is_user_defined(self, var_name):
        # Get a list of system environment variable names
        system_vars = set(os.environ.keys()) - set(self.user_defined_vars())
        # Check if the variable is not a system variable
        return var_name not in system_vars

    def user_defined_vars(self):
        # Get a list of user-defined environment variable names
        return ["SystemRoot", "ALLUSERSPROFILE"]  # Add more variables if needed



    def set_environment_variable(self):
        var_name = self.var_name_entry.get()
        var_value = self.var_value_entry.get()

        if not var_name:
            messagebox.showerror("Error", "Please enter a variable name.")
            return

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, var_name, 0, winreg.REG_SZ, var_value)
            winreg.CloseKey(key)
            os.environ[var_name] = var_value
            messagebox.showinfo("Success", f"Environment variable '{var_name}' set successfully.")
            self.populate_listbox() 
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set environment variable: {e}")

    def clear_entries(self):
        self.var_name_entry.delete(0, tk.END)
        self.var_value_entry.delete(0, tk.END)

    def delete_selected(self):
        selected_vars = [var_name for var_name, var_checkbox in self.checkboxes.items() if var_checkbox.instate(['selected'])]
        if not selected_vars:
            messagebox.showerror("Error", "No variables selected.")
            return

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
            for var_name in selected_vars:
                winreg.DeleteValue(key, var_name)
                os.environ.pop(var_name, None)
                self.checkboxes[var_name].destroy()
                del self.checkboxes[var_name]
            winreg.CloseKey(key)
            messagebox.showinfo("Success", "Selected environment variables deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete environment variables: {e}")

root = tk.Tk()
app = EnvironmentVariableEditor(root)
root.mainloop()
