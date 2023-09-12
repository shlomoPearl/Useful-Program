import fitz
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.ttk import *


def click(event):
    # Here retrieving the size of the parent
    # widget relative to master widget
    x = event.x_root - window.winfo_rootx()
    y = event.y_root - window.winfo_rooty()

    # Here grid_location() method is used to
    # retrieve the relative position on the
    # parent widget
    z = window.grid_location(x, y)

    # printing position
    print(z)


def scroll_text(event):
    page_input.xview_scroll(int(-1 * (event.delta / 120)), "units")


def get_input(page_entry, output_entry):
    page_list = page_entry.get().replace(' ', '').split(',')
    page_list = [x for x in page_list if x != '']
    print(page_list)
    print(output_entry.get() + '.pdf')


window = tk.Tk()
window.geometry('400x200')
# window.columnconfigure(1, weight=2)
# window.columnconfigure(2, weight=3)

page_label = tk.Label(
    text="Enter the page numbers you want to delete (with ',' between each number): "
)
page_label.grid(row=0, column=0, sticky='w', columnspan=8)

page_input = tk.Entry(width=65)
page_input.grid(row=1, column=0, sticky='w', columnspan=8)

range_label = tk.Label(
    text="Enter the range of pages you want to delete:"
)
range_label.grid(row=2, column=0, sticky='w', columnspan=5, pady=10)
from_input = tk.Entry(width=5)
hyphen_label = tk.Label(text="-")
to_input = tk.Entry(width=5)
from_input.grid(row=2, column=1, sticky='e')
hyphen_label.grid(row=2, column=2)
to_input.grid(row=2, column=3, sticky='w')

output_label = tk.Label(text="Enter the new file name:")
output_label.grid(row=3, column=0, sticky='w', pady=10)
output_file = tk.Entry(window)
output_file.grid(row=3, column=1, sticky='w')
end_label = tk.Label(text=".pdf")
end_label.grid(row=3, column=1, sticky='e')

button = tk.Button(
    text="Done!",
    command=lambda: get_input(page_input, output_file)
)
button.grid(row=4, column=1, sticky='s')

# filename = fd.askopenfilename()
# print(filename)

# window.bind("<Button-1>", click)
window.mainloop()


# file_handle = fitz.open(input_file)
#
# # for i in range(5,18):
# #     pages_delete.append(i)
# # for i in range(69,79):
# #     pages_delete.append(i)
# pages_keep = []
# for i in range(26):
#     if i not in pages_delete:
#         pages_keep.append(i)
# print(pages_delete)
# file_handle.select(pages_keep)
#
# file_handle.save(output_file)
