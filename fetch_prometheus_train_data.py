import requests
import csv
import json
import urllib

consolidate_book = "final_stats.csv"
consolidate = open(consolidate_book, 'w')
servers = ['abc.com']
workbook = csv.writer(consolidate)
workbook.writerow(["time", "memory", "cpu", "inbw", "outBw", "disk"])

query_url = "http://prometheus-dev.com:9090/api/v1/query"
range_url = "http://prometheus-dev.com:9090/api/v1/query_range"

for server in servers:
    try:
        
        server_name = server.split('.')[0].strip()
        books = open(server_name + '.csv', 'w')
        target = server.strip() + ':9100'
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nTarget is {}\n".format(target))

        chapter = csv.writer(books)
        chapter.writerow(["time", "memory", "cpu", "inbw", "outBw", "disk"])
        step = 0

        query_data = 'query=node_memory_MemTotal_bytes{instance="' + target + '"}[1d]'
        queryData = urllib.quote_plus(query_data, '=')
        response = requests.get(query_url, params=queryData)
        print(response.status_code)
        #print(response.text)
        op = json.loads(response.text)
        results = response.json()['data']['result']
        print(results)
        value_bucket1 = results[0]['values']
        #print(value_bucket)
        print(value_bucket1[0][0])
        print(value_bucket1[-1][0])
        end_index = value_bucket1[-1][0]
        step = int(value_bucket1[1][0]) - int(value_bucket1[0][0])
        if step == 0:
            print("ERROR: incorrect step values.Please check the data: {}".format(value_bucket1[:5]))
            break
        else:
            print("STEP values is {}\n".format(step))

        query_data = 'query=node_memory_MemFree_bytes{instance="' + target + '"}[1d]'
        queryData = urllib.quote_plus(query_data, '=')
        response2 = requests.get(query_url, params=queryData)
        print(response2.status_code)
        #print(response2.text)
        op = json.loads(response2.text)
        results = response2.json()['data']['result']
        print(results)
        value_bucket2 = results[0]['values']
        #print(value_bucket)
        print(value_bucket2[0][0])
        print(value_bucket2[-1][0])
        if step != (int(value_bucket2[1][0]) - int(value_bucket2[0][0])):
            print("ERROR: incorrect step values.Please check the data: {}".format(value_bucket2[:5]))
            break

        query_data = 'query=node_memory_Cached_bytes{instance="' + target + '"}[1d]'
        queryData = urllib.quote_plus(query_data, '=')
        response3 = requests.get(query_url, params=queryData)
        print(response3.status_code)
        #print(response.text)
        op = json.loads(response3.text)
        results = response3.json()['data']['result']
        #print(results)
        value_bucket3 = results[0]['values']
        #print(value_bucket)
        print(value_bucket3[0][0])
        print(value_bucket3[-1][0])
        if step != (int(value_bucket3[1][0]) - int(value_bucket3[0][0])):
            print("ERROR: incorrect step values.Please check the data: {}".format(value_bucket3[:5]))
            break


        query_data = 'query=node_memory_Buffers_bytes{instance="' + target + '"}[1d]'
        queryData = urllib.quote_plus(query_data, '=')
        response4 = requests.get(query_url, params=queryData)
        print(response4.status_code)
        #print(response.text)
        op = json.loads(response4.text)
        results = response4.json()['data']['result']
        #print(results)
        value_bucket4 = results[0]['values']
        #print(value_bucket4)
        print(value_bucket4[0][0])
        print(value_bucket4[-1][0])        
        start_index = value_bucket4[0][0]
        if step != (int(value_bucket4[1][0]) - int(value_bucket4[0][0])):
            print("ERROR: incorrect step values.Please check the data: {}".format(value_bucket4[:5]))
            break

        if start_index != value_bucket1[0][0]:
            delta = int(start_index) - int(value_bucket1[0][0])
            del(value_bucket1[:delta])   
        if start_index != value_bucket2[0][0]:
            delta = int(start_index) - int(value_bucket2[0][0])
            del(value_bucket2[:delta])
        if start_index != value_bucket3[0][0]:
            delta = int(start_index) - int(value_bucket3[0][0])
            del(value_bucket3[:delta])

        if end_index != value_bucket2[-1][0]:
            delta = int(value_bucket2[-1][0]) - int(end_index)
            del(value_bucket2[-delta:])
        if end_index != value_bucket3[-1][0]:
            delta = int(value_bucket3[-1][0]) - int(end_index)
            del(value_bucket3[-delta:])
        if end_index != value_bucket4[-1][0]:
            delta = int(value_bucket4[-1][0]) - int(end_index)
            del(value_bucket4[-delta:])

        print(len(value_bucket1))
        print(len(value_bucket2))
        print(len(value_bucket3))
        print(len(value_bucket4))

        if (len(value_bucket1) != len(value_bucket2) or len(value_bucket1) != len(value_bucket3) or len(value_bucket1) != len(value_bucket4)):
            print("Error in data massaging.Please check the data.")
            break

        start_index = int(start_index)
        end_index = int(end_index)
        print("\n#########################################\nStart index is {}".format(start_index))
        print("End index is {}".format(end_index))
        print("\n#########################################\n")

        #Calculate memory consumption and fill csv
        ####################################
        # Step 1: Get Memory stats
        # Fromula: ((node_memory_MemTotal - (node_memory_MemFree + node_memory_Cached + node_memory_Buffers)) / node_memory_MemTotal) * 100.0
        ####################################
        for index in range(len(value_bucket1)):
            snapshot = [] 
            timestamp = value_bucket1[index][0]
            snapshot.append(timestamp)

            node_memory_MemTotal = int(value_bucket1[index][1])
            node_memory_MemFree = float(value_bucket2[index][1])
            node_memory_Cached = int(value_bucket3[index][1])
            node_memory_Buffers = int(value_bucket4[index][1])
            print("node_memory_MemTotal {} and node_memory_MemFree {}".format(node_memory_MemTotal, node_memory_MemFree))

            mem_consumption = ((node_memory_MemTotal - (node_memory_MemFree + node_memory_Cached + node_memory_Buffers)) / node_memory_MemTotal) * 100.0
            #chapter.writerow([timestamp, mem_consumption])
            snapshot.append(mem_consumption)
            chapter.writerow(snapshot)   
        books.close()
    except Exception as e:
        print("Failed with error {} \n".format(e))
    
    
"""
dump
"""
consolidate.close()
