# ! READ ME !
# Replace ",;" to ";"
# The CSV contains an extra comma separator at the end of every field

# dict_Auths(AutorName: [id, [Paper1, Paper2, ...], PageRank-index, H-index, Collab-Score, Diversity-Score, NoofTimeCited])
# dict_Papers(PaperIndex: [PaperTitle, [Author1, Author2, ...], [Citation1, Citation2, ...]])

import networkx as nx
 
graph = nx.DiGraph()
 
dict_Auths = {}
dict_Papers = {}
dict_Id2Auths = {}
list_cita = []
    
int_Auth_index = 0
 
inputFile = open("../../Dataset/CSV/outputacmCSV.csv")
# inputFile = open("../../Dataset/CSV/shortCSVFile.csv")

print("--Creating Dictionaries--")


for line in inputFile:
    entry = line.split(';')
    int_Paper_index = entry[0]
    str_paper_name = entry[1]
    list_cita = []
    list_temp_Auth = []

    # Creating Dictionary entries for Citations
    for int_citedPaper in entry[3].split(','):
        list_cita.append(int_citedPaper)
        if int_citedPaper not in dict_Papers.keys():
            dict_Papers[int_citedPaper] =[]
            dict_Papers[int_citedPaper].append("--NA--")
            dict_Papers[int_citedPaper].append([])
            dict_Papers[int_citedPaper].append([])

    # Populating Author Dictionary
    for str_auth_name in entry[2].split(','):
        if str_auth_name not in dict_Auths.keys():
            dict_Auths[str_auth_name] = []
            dict_Auths[str_auth_name].append(int_Auth_index)
            list_papers = []
            list_papers.append(entry[0])
            dict_Auths[str_auth_name].append(list_papers)
            dict_Auths[str_auth_name].append(0)
            dict_Id2Auths[int_Auth_index] = str_auth_name
            int_Auth_index += 1
        else:
            dict_Auths[str_auth_name][1].append(entry[0])
        list_temp_Auth.append(dict_Auths[str_auth_name][0])
    
    # Populating Papers Dictionary
    if int_Paper_index not in dict_Papers.keys():
        dict_Papers[int_Paper_index] =[]
        dict_Papers[int_Paper_index].append(str_paper_name)
        dict_Papers[int_Paper_index].append(list_temp_Auth)
        dict_Papers[int_Paper_index].append(list_cita)
    else:
        dict_Papers[int_Paper_index][0] = str_paper_name
        dict_Papers[int_Paper_index][1] = list_temp_Auth
        dict_Papers[int_Paper_index][2] = list_cita





#--------------------------------Making Graph and getting ranks -----------------------------------------
 
print("--Making Graph--")
for source in dict_Papers:
    for destination in dict_Papers[source][2]:
        graph.add_edge(source,destination)
 
dict_ranks = nx.pagerank(graph)


#------------------------------- Distributing Paper Ranks -----------------------------------------
 
print("--Distributing Ranks--")
int_zeroPaperRank = 0
int_max_pr = -1
 
for paper in dict_ranks:
    if dict_ranks[paper] is 0:
        int_zeroPaperRank += 1
    if paper in dict_Papers:
        int_position = 1
        int_noOfAuthors = len(dict_Papers[paper][1])
        for int_id_author in dict_Papers[paper][1]:
            int_weight = (int_noOfAuthors-int_position+1)/(0.5*int_noOfAuthors*(int_noOfAuthors+1))
            int_tempRank = dict_ranks[paper]*int_weight *1000000
            if (int_tempRank > int_max_pr):
                int_max_pr = int_tempRank
            dict_Auths[dict_Id2Auths[int_id_author]][2] += int_tempRank
                                                            
                                                            #dict_Auths[Author][2] --> PageRank-index

int_zeroAuthorRank = 0

for author in dict_Auths:
    if dict_Auths[author][2] is 0.0:
        int_zeroAuthorRank += 1
 
 
# print("Total No. of Authors: ",len(dict_Auths))
# print("No. of Authors with rank 0: ",int_zeroAuthorRank)
 
# print("Total No. of Papers: ",len(dict_Papers))
# print("No. of Papers with rank 0: ",int_zeroPaperRank)
 
  
#----------------------------------Calculating H indexes--------------------------

print("--Calculating H-index--")

int_max_Hindex = -1

for author in dict_Auths:
    list_papers = dict_Auths[author][1]
    h_index = 0
    int_paperCount=0
    list_Hindex = []
    for paper in list_papers:
        list_Hindex.append(graph.in_degree(paper))
    list_Hindex.sort(reverse=True)
    for number in list_Hindex:
        int_paperCount += 1
        if number >= int_paperCount:
            h_index += 1
    if h_index > int_max_Hindex:
        int_max_Hindex = h_index
    dict_Auths[author].append(h_index)                      #dict_Auths[Author][3] --> H-index

#-------------------------------Finding Collaboration Score-------------------#

print("--Collaboration Score--")

for author in dict_Auths:
    int_collab_score = 0
    for paper in dict_Auths[author][1]:
        int_collab_score += len(dict_Papers[paper][1])-1
    if len(dict_Auths[author][1]) is not 0:
        int_collab_score = int_collab_score/len(dict_Auths[author][1])
    dict_Auths[author].append(int_collab_score)             #dict_Auths[Author][4] --> Collab-Score
 
#-----------------------------Finding Diversity Score------------------------#

print("--Diversity Score--")

for author in dict_Auths:
    list_diverse_authors = []
    for paper in dict_Auths[author][1]:
        for cita in dict_Papers[paper][2]:
            for auth in dict_Papers[cita][1]:
                if auth not in list_diverse_authors:
                    list_diverse_authors.append(auth)

    int_diversity_score = len(list_diverse_authors)
    dict_Auths[author].append(int_diversity_score)          #dict_Auths[Author][5] --> Diversity-Score

#-------------------------------------------------------------------------------------

for author in dict_Auths.keys():
    cited = 0
    for paper in dict_Auths[author][1]:
        cited += graph.in_degree(paper)
    dict_Auths[author].append(cited)

#-----------------------------------Sorting Author(w.r.t H-Index && PageRanks)--------------------------

# # print()
# # count = 0
# # print("Authors Sorted According to H-Index:")
# # print()
# # for entry in sorted(dict_Auths.values(), key = lambda x:x[3], reverse = True):
# #     if count == 20:
# #         break
# #     print("     ",str(entry[0]).ljust(10)," ", dict_Id2Auths[entry[0]].ljust(20), "   %.7f" %entry[2],'    ',entry[3], "   %.7f" %entry[4])
# #     count += 1
# # print()


# # print()
# # print("Authors Sorted According to PageRank:")
# # print()
# # count = 0
# # for entry in sorted(dict_Auths.values(), key = lambda x:x[2], reverse = True):
# #     if count == 20:
# #         break
# #     print("     ",str(entry[0]).ljust(10)," ", dict_Id2Auths[entry[0]].ljust(20), "   %.7f" %entry[2],'    ',entry[3], "   %.7f" %entry[4])
# #     count += 1
# # print()

# ---------------------------------------------

# print("--Writing to File--")

# print("int_max_Hindex = ", int_max_Hindex)
# print("int_max_pr = ", int_max_pr)
# print("dict_Papers = ", dict_Papers)
# print("##############################################################################")
# print("dict_Auths = ", dict_Auths)
# print("##############################################################################")
# print("dict_Id2Auths = ", dict_Id2Auths)


# sum = 0
# count = 0
# for author in dict_Auths.keys():
#     if dict_Auths[author][5] is 0:
#         continue
#     print(author, " -- ","D : ", dict_Auths[author][5])
#     sum += dict_Auths[author][5]
#     count += 1

# print("Average Diversity Score: ", sum/count)