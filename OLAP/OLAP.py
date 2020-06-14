#!/usr/bin/env python3
#encoding=utf8
import argparse
import os
import sys
import csv

def OLAP(args):
    output_dict={}
    capped = False
    OTHER_list = []

    if(args.group_by):
        OTHER_list = group_by(output_dict, args)

    if(args.top):
        capped = top(output_dict, args, OTHER_list)

    if(args.min):
        Min(output_dict, args, OTHER_list)

    if(args.max):
        Max(output_dict, args, OTHER_list)

    if(args.sum):
        Sum(output_dict, args, args.sum, OTHER_list)

    if(args.count or not args.group_by):
        count(output_dict, args, OTHER_list)

    if(args.mean):
        mean(output_dict, args, OTHER_list)


    sorted_keys = keySorter(args, capped)

    for k in sorted_keys:
        if (k not in output_dict.keys()):
            sorted_keys.remove(k)

    sorted_dict = {}
    for k in sorted_keys:
        try:
            sorted_dict[k] = output_dict[k]
        except KeyError:
            continue
    if(len(sorted_keys)>0):
        printCSV(sorted_keys, sorted_dict)

#creates, initiates and returns a dictionary with group-by categories for keys
def mkDict(output_dict, args):
    dict = {}
    for k in output_dict[args.group_by]:
        dict[k] = [] 
    return dict  

#finds a key in the given csv file that is identical to the given header argument
def keyFinder(reader, header):
    for row in reader:
        break
    returnKey = ''
    for k in row.keys():
        if (UTF(k)==header.lower()):
            returnKey = k
            break
    return returnKey
    
#reopens and rereads the file given
def reopenf(args, file):
    file.close()
    file=open(args.input, mode = "r")
    reader = csv.DictReader(file)
    return reader

#stdouts the given dictionart in a CSV format
def printCSV(sorted_keys, sorted_dict):
    writer = csv.DictWriter(sys.stdout, fieldnames=sorted_keys)

    writer.writeheader()
    pos = 0
    sorted_dict.keys()
    
    while(pos < len(sorted_dict[sorted_keys[0]])):
        tmp_dict = {}
        for k in sorted_keys:
            if(pos<len(sorted_dict[sorted_keys[0]])):
                tmp_dict[k] = sorted_dict[k][pos]
            else:
                tmp_dict[k] = None
        writer.writerow(tmp_dict)
        pos += 1

#sorts the keys in the order of the sequence the user requested
def keySorter(args, capped):

    sorted_keys = []

    if(args.group_by):
        sorted_keys.append(args.group_by)

    if(args.count):
        sorted_keys.append("count")

    if(args.min):
        for arg in args.min:
            header = "min_" + arg
            sorted_keys.append(header)

    if(args.max):
        for arg in args.max:
            header = "max_" + arg
            sorted_keys.append(header)

    if(args.sum):
        for arg in args.sum:
            header = "sum_" + arg
            sorted_keys.append(header)

    if(args.mean):
        for arg in args.mean:
            header = "mean_" + arg
            sorted_keys.append(header)

    if(args.top):
        header = "top_" + args.top[1]
        if capped:
            header += "_capped"
        sorted_keys.append(header)

    if(len(sorted_keys)==0):
        sorted_keys.append('count')
    return sorted_keys

#changes a string in Unicode Transformation Format
def UTF(s):
    return s.encode("utf-8").decode("utf-8-sig").rstrip().lower()

#groups values in the requested field into distinct categories
def group_by(output_dict, args):
    output_dict[args.group_by] = []

    f=open(args.input, mode = "r")
    reader = csv.DictReader(f)
    
    group_by_key = keyFinder(reader, args.group_by)
    reader = reopenf(args, f)
    categories = []
    for row in reader:
        try: 
            if(row[group_by_key] not in categories):
                categories.append(row[group_by_key])
        except:
            print("​Error: "+args.input+":no group-by argument with name "+args.group_by+" found", file=sys.stderr)
            exit(9)

    categories.sort()
    output_dict[args.group_by] = categories

    OTHER_list = []
    if(args.limit_to):
        if (len(output_dict[args.group_by])>args.limit_to):  
            print("​Error: "+args.input+":"+ args.group_by +" has been capped at "+str(args.limit_to)+" distinct values", file=sys.stderr)
            print("​Error: "+args.input+":"+"group-by argument "+ args.group_by+ " has high cardinality", file=sys.stderr)
            OTHER_list = output_dict[args.group_by][args.limit_to:]
            del output_dict[args.group_by][args.limit_to:]
            output_dict[args.group_by].append('_OTHER')

    f.close()
    return OTHER_list

# compute the ​top k ​most common values of categorical-field-name
def top(output_dict, args, OTHER_list):
    header = 'top_'+args.top[1]
    output_dict[header] = []
    capped = False

    f=open(args.input, mode = "r")
    reader = csv.DictReader(f)

    top_key = keyFinder(reader, args.top[1])
    reader = reopenf(args, f)

    visitedVal = []
    for row in reader:
        try:
            if (row[top_key] not in visitedVal):
                visitedVal.append(row[top_key])
        except KeyError:
            print("​Error: "+args.input+":no field with name "+args.top[1]+" found", file=sys.stderr)
            exit(8)

    reader = reopenf(args, f)
    try:
        if(int(args.top[0])>20 or len(visitedVal)>20):
            capped = True
            header += "_capped"
            output_dict[header] = []
            print("​Error: "+args.input+":"+args.top[1]+" has been capped at 20 distinct values", file=sys.stderr)
            if(len(visitedVal)>20):
                print("​Error: "+args.input+":"+"top k argument "+ args.top[1]+ " has high cardinality", file=sys.stderr)

    except ValueError:
        print("​Error: "+args.input+":second top argument with name "+args.top[0]+" is not a number", file = sys.stderr)
        exit(6)

    if(args.group_by):
        group_by_key = keyFinder(reader, args.group_by)
        reader = reopenf(args, f)

        top_dict = mkDict(output_dict, args)

        for row in reader:
            category = row[group_by_key]
            if(category not in OTHER_list):
                if(row[top_key] not in top_dict[category]):
                    top_dict[category].append(row[top_key])
            else:
                if(row[top_key] not in top_dict['_OTHER']):
                    top_dict['_OTHER'].append(row[top_key])
        
        count_dict = top_counter(output_dict, args, top_dict, OTHER_list)

        for category in top_dict.keys():
            string = ''
            i = 0
            cap=int(args.top[0])
            if (cap>20):
                cap = 20
            while(i< cap):
                largest = max(count_dict[category])
                if(largest == 0):
                    break
                pos = count_dict[category].index(largest)
                string += str(top_dict[category][pos]) + ': ' + str(count_dict[category][pos]) + ','
                count_dict[category][pos] = 0
                i+=1
            output_string = string[:-1]
            output_dict[header].append(output_string)


    else:
        top_dict = {}
        top_dict['All'] = []
        top_list = top_dict['All']
        for row in reader:
            if(row[top_key] not in top_list):
                top_list.append(row[top_key])

        count_dict = top_counter(output_dict, args, top_dict, OTHER_list)
        count_list = count_dict['All']
        j=0
        output_string = ''
        while(j< int(args.top[0])):
            if(len(count_list)==0):
                break
            else:
                pos = count_list.index(max(count_list))
            output_string += (top_list[pos] + ': ' + str(count_list[pos]) + ',')
            del count_list[pos]
            del top_list[pos]
            j+=1
        output_string = output_string[:-1]
        output_dict[header].append(output_string)
    f.close()

    return capped

# A helper function to count the number of records for each category
def top_counter(output_dict, args, top_dict, OTHER_list):
    if(args.group_by):
        count_dict = mkDict(output_dict, args)
    else:
        count_dict = {'All':[]}
    for category in top_dict.keys():
        f=open(args.input, mode = "r")
        reader = csv.DictReader(f)

        if(args.group_by):
            group_by_key = keyFinder(reader, args.group_by)

        top_key = keyFinder(reader, args.top[1])
        reader = reopenf(args, f)

        i=0
        while(i<len(top_dict[category])):
            count_dict[category].append(0)
            i+=1

        if(category != '_OTHER'):

            for row in reader:
                if(args.group_by):
                    if(row[group_by_key] == category and row[top_key] in top_dict[category]):
                        pos = top_dict[category].index(row[top_key])
                        count_dict[category][pos] += 1

                elif(row[top_key] in top_dict[category]):
                    pos = top_dict[category].index(row[top_key])
                    count_dict[category][pos] += 1

        else:
            for row in reader:
                if(args.group_by):
                    if(row[group_by_key] in OTHER_list and row[top_key] in top_dict[category]):
                        pos = top_dict[category].index(row[top_key])
                        count_dict[category][pos] += 1
                elif(row[top_key] in top_dict[category]):
                    pos = top_dict[category].index(row[top_key])
                    count_dict[category][pos] += 1

    return count_dict
    f.close()

#compute the ​minimum​ value of numeric-field-name
def Min(output_dict, args, OTHER_list):
    for header in args.min:
        output_dict['min_' + header] = []
        f = open(args.input, "r")
        reader = csv.DictReader(f)
        kMin = keyFinder(reader, header)
        reader = reopenf(args, f)
        if(args.group_by):
            line = 1
            nonNumeric = 0
            min_dict = mkDict(output_dict, args)
            kGroup = keyFinder(reader, args.group_by)
            for row in reader:
                line += 1
                try:
                    if(row[kGroup] in min_dict.keys()):
                        min_dict[row[kGroup]].append(float(row[kMin]))
                    elif(row[kGroup] in OTHER_list):
                        min_dict['_OTHER'].append(float(row[kMin]))
                except ValueError:
                    print("Error: "+args.input+":"+str(line)+": can’t compute min on non-numeric value "+"'"+row[kMin]+"'", file=sys.stderr)
                    nonNumeric += 1
                    if(nonNumeric > 100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)

            for k in min_dict.keys():
                if(len(min_dict[k])>0):
                    output_dict['min_' + header].append(min(min_dict[k]))
                else:
                    output_dict['min_' + header].append('NaN')

        else:
            line = 1
            nonNumeric = 0
            values = []
            for row in reader:
                line += 1
                try:
                    values.append(float(row[kMin]))
                except ValueError:
                    print("Error: "+args.input+":"+str(line)+": can’t compute min on non-numeric value "+"'"+row[kMin]+"'", file=sys.stderr)
                    nonNumeric += 1
                    if(nonNumeric > 100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)

            if(len(values)>0):
                output_dict['min_' + header].append(min(values))
            else:
                output_dict['min_' + header].append('NaN')
        f.close()

#compute the ​maximum​ value of numeric-field-name
def Max(output_dict, args, OTHER_list):
    for header in args.max:
        output_dict['max_' + header] = []
        f = open(args.input, "r")
        reader = csv.DictReader(f)
        kMax = keyFinder(reader, header)
        reader = reopenf(args, f)

        if(args.group_by):
            line = 1
            nonNumeric = 0
            max_dict = mkDict(output_dict, args)
            kGroup = keyFinder(reader, args.group_by)
            for row in reader:
                line += 1
                try:
                    if(row[kGroup] in max_dict.keys()):
                        max_dict[row[kGroup]].append(float(row[kMax]))
                    elif(row[kGroup] in OTHER_list):
                        max_dict['_OTHER'].append(float(row[kMax]))
                except ValueError:
                    print("Error: "+args.input+":"+str(line)+": can’t compute min on non-numeric value "+"'"+row[kMax]+"'", file=sys.stderr)
                    nonNumeric += 1
                    if(nonNumeric > 100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)

            for k in max_dict.keys():
                if(len(max_dict[k])>0):
                    output_dict['max_' + header].append(max(max_dict[k]))
                else:
                    output_dict['max_' + header].append('NaN')
        
        else:
            line = 1
            nonNumeric = 0
            values = []
            for row in reader:
                line += 1
                try:
                    values.append(float(row[kMax]))
                except ValueError:
                    print("Error: "+args.input+":"+str(line)+": can’t compute min on non-numeric value "+"'"+row[kMax]+"'", file=sys.stderr)
                    nonNumeric += 1
                    if(nonNumeric > 100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)
            if(len(values)>0):
                output_dict['max_' + header].append(max(values))
            else:
                output_dict['max_' + header].append('NaN')

    f.close()

#count​ the number of records
def count(output_dict, args, OTHER_list):
    output_dict['count'] = []
    f = open(args.input, "r")
    reader = csv.DictReader(f)
    if(args.group_by):
        kGroup = keyFinder(reader, args.group_by)
        reader = reopenf(args, f)
        
        count_dict = mkDict(output_dict, args)
        tmp_count = 0
        count = 0
        for row in reader:    
            if (row[kGroup] in output_dict[args.group_by]):
                if(count_dict[row[kGroup]] == []):
                    count_dict[row[kGroup]] = 1
                else:
                    count_dict[row[kGroup]] +=1
            elif(row[kGroup] in OTHER_list):
                if(count_dict['_OTHER'] == []):
                    count_dict['_OTHER'] = 1
                else:
                    count_dict['_OTHER'] +=1        

        for k in count_dict:
            output_dict['count'].append(count_dict[k])
    
    else:
        count = 0
        for row in reader:
            count+=1

        output_dict['count'].append(count)

    f.close()

#compute the ​ sum​ of numeric-field-name
def Sum(output_dict, args, fields_to_sum, OTHER_list):
    for header in fields_to_sum:
        output_dict['sum_' + header] = []
        f = open(args.input, "r")
        reader = csv.DictReader(f)

        kSum = keyFinder(reader, header) 
        reader = reopenf(args, f)

        if(args.group_by):

            kGroup = keyFinder(reader, args.group_by) 
            reader = reopenf(args, f)
            sum_dict = mkDict(output_dict, args)
            line = 1
            nonNumeric = 0
            for row in reader:
                line +=1
                try:
                    if (row[kGroup] in output_dict[args.group_by]):
                        if(sum_dict[row[kGroup]] == []):
                            sum_dict[row[kGroup]] = float(row[kSum])
                        else:
                            sum_dict[row[kGroup]] += float(row[kSum])
                    elif(row[kGroup] in OTHER_list):
                        if(sum_dict['_OTHER'] == []):
                            sum_dict['_OTHER'] = float(row[kSum])
                        else:
                            sum_dict['_OTHER'] += float(row[kSum])
                except ValueError:
                    if(args.sum and header in args.sum):
                        print("Error: "+args.input+":"+str(line)+": can’t compute sum on non-numeric value "+"'"+row[kSum]+"'", file=sys.stderr)
                    else:
                        print("Error: "+args.input+":"+str(line)+": can’t compute mean on non-numeric value "+"'"+row[kSum]+"'", file=sys.stderr)
                    nonNumeric+=1
                    if(nonNumeric>100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)

            for k in sum_dict:
                if(type(sum_dict[k]) != list):
                    output_dict['sum_' + header].append(sum_dict[k])
                else:
                    
                    output_dict['sum_' + header].append('NaN')

        else:
            SUM = 0
            line = 1
            nonNumeric = 0
            for row in reader:
                line += 1
                try:
                    SUM += float(row[kSum])
                except ValueError:
                    if(args.sum and header in args.sum):
                        print("Error: "+args.input+":"+str(line)+": " "can’t compute sum on non-numeric value "+row[kSum], file=sys.stderr)
                    else:
                        print("Error: "+args.input+":"+str(line)+": " "can’t compute mean on non-numeric value "+row[kSum], file=sys.stderr)
                    nonNumeric+=1
                    if(nonNumeric>100):
                        print("Error: "+args.input+":more than 100 non-numeric values found in aggregate column "+header, file=sys.stderr)
                        sys.exit(7)
                except KeyError:
                    print("​Error: "+args.input+":no field with name "+header+" found", file=sys.stderr)
                    exit(8)

            if(type(SUM) != int):
                output_dict['sum_' + header].append(SUM)
            else:
                output_dict['sum_' + header].append('NaN')

    f.close()

#compute the ​mean​ (average) of numeric-field-name
def mean(output_dict, args, OTHER_list):
    if(not args.sum):
        Sum(output_dict, args, args.mean, OTHER_list)
    if(not args.count):
        count(output_dict, args, OTHER_list)

    for i in args.mean:
        pos=0
        output_dict['mean_' + i] = []
        while(pos<len(output_dict['count'])):
            try:
                MEAN = output_dict['sum_' + i][pos] / output_dict['count'][pos]
            except TypeError:
                MEAN = 'NaN'
            output_dict['mean_' + i].append(MEAN)
            pos+=1