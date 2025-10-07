import csv

def extract_csv_data(csv_file):

    # Initialize empty lists
    list_1d = []
    list_2d = []

    # Read the CSV file
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        is_1d = True
        for row in reader:
            if row[0] == "pi":
                continue
            elif row[0] == "cij":
                is_1d = False
                continue
            if is_1d:
                list_1d = [int(x) for x in row]
            else:
                list_2d.append([int(x) for x in row])
    
    return (list_1d, list_2d)
