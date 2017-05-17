import pandas as pd
import re
import glob
from math import nan

from makeDataFunctions.makeUniqueIds import getIds

"""
Merging Data from the Database into one Dataframe

NOT GLOBBING ANYMORE AND SINCE TOOK TOO LONG
"""

# def mergePerson():
#
#     #combine the Person Data using Glob
#     path = 'dbCSVdata/Person'  # use your path
#     allFiles = glob.glob(path + "/*.csv")
#     personDf = pd.DataFrame()
#     dfs = []
#     for file_ in allFiles:
#         df = pd.read_csv(file_, index_col=None, header=0)
#         dfs.append(df)
#         personDf = pd.concat(dfs)
#
#     personDf.to_csv('fullCSVtables/Person')
#
# def mergeCustomer():
#
#     #combine the Person Data using Glob
#     path = 'dbCSVdata/Customer'  # use your path
#     allFiles = glob.glob(path + "/*.csv")
#     personDf = pd.DataFrame()
#     dfs = []
#     for file_ in allFiles:
#         df = pd.read_csv(file_, index_col=None, header=0)
#         dfs.append(df)
#         personDf = pd.concat(dfs)
#
#     personDf.to_csv('fullCSVtables/Customer')
#
# def mergeCustomerRep():
#
#     #combine the Person Data using Glob
#     path = 'dbCSVdata/CustomerRep'  # use your path
#     allFiles = glob.glob(path + "/*.csv")
#     personDf = pd.DataFrame()
#     dfs = []
#     for file_ in allFiles:
#         df = pd.read_csv(file_, index_col=None, header=0)
#         dfs.append(df)
#         personDf = pd.concat(dfs)
#
#     personDf.to_csv('fullCSVtables/CustomerRep')

"""Get all types of words"""
negWords = getIds('storedData/words/negativeWords.csv', False)
posWords = getIds('storedData/words/positiveWords.csv', False)
stopWords = getIds('storedData/words/stopWords.csv', False)

def tidyTextTable():
    textDf= pd.read_csv('fullCSVtables/Text.csv')

    #add a column for each positive and negative word
    allWords= negWords+posWords
    for word in allWords:
        textDf[word]=0


    #add count cols to the Df
    for wordCol in allWords:
        textDf[wordCol]= 0

    textDf.info()

    #count the words
    textDf= textDf.apply(countWords, axis=1)
    textDf=textDf.drop('TEXT', axis=1)

    #melt the word count columns
    # melt platform count for Person
    id_vars = ['idText', 'idConversation', 'personId']
    textDf = pd.melt(textDf, id_vars=id_vars, value_vars=allWords,
                       var_name='KEYWORD', value_name='WORD_COUNT')

    return textDf


def countWords(textDf):
    allWords = negWords + posWords

    #get the text for this row
    textData= textDf.TEXT
    textData=textData[1:].split(' ')

    #count the no stop words
    i=0
    wordCountDict = {}
    for word in allWords:
        wordCountDict[word]=0
        i+=1

    for word in textData:
        if word in allWords:
            wordCountDict[word]= wordCountDict[word]+1

    #set the count for the new df
    for word in allWords:
        count= wordCountDict[word]
        textDf[word]= count

    return textDf



def tidyConvoTable():
    convoDf = pd.read_csv('fullCSVtables/Conversation.csv')

    #make one bool Col for is_call instead of text too
    convoDf = convoDf.drop(labels='IS_TEXT_CHAT', axis=1)

    #bool-> binary encoding
    convoDf['IS_CALL']= convoDf['IS_CALL'].astype(int)

    return convoDf


def tidyPersonTable():

    personDf= pd.read_csv('fullCSVtables/Person.csv', index_col=0)

    # normalize phone number
    personDf['AREA_CODE'] = personDf['PHONE NUMBER'].apply(getAreaCode)
    personDf['PHONE NUMBER'] = personDf['PHONE NUMBER'].apply(normalizePhone)

    #melt platform count for Person
    id_vars= ['idPerson' ,'FIRST_NAME' ,'MIDDLE INITIAL', 'LAST_NAME','UTC_TIMEZONE','EMAIL', 'AREA_CODE', 'PHONE NUMBER']
    personDf=personDf.rename( columns={'PLATFORM_A_CONVO_COUNT':'A', 'PLATFORM_B_CONVO_COUNT':'B', 'PLATFORM_C_CONVO_COUNT':'C'})

    personDf= pd.melt(personDf, id_vars=id_vars, value_vars=['A','B','C'],
                      var_name='PLATFORM', value_name='CONVO_COUNT')

    #get area codes. Most are American
    print(personDf.head())

    return personDf

#get rid of non digits in phone num
def normalizePhone(phoneNum):
    normalizeNum= re.sub('[^0-9]', '', phoneNum)

    length= len(normalizeNum)

    #return NaN if incomplete phone number
    if length<10:
        return nan

    #find are code if has one
    elif length>10:
        endIndx=  length- 10
        phoneNum= normalizeNum[endIndx:]

    #get the normalized phoen number
    else:
        phoneNum=normalizeNum

    return phoneNum

#get the area code in the Phone Collumn
def getAreaCode(phoneNum):
    normalizeNum= re.sub('[^0-9]', '', phoneNum)

    length= len(normalizeNum)

    #return NaN if incomplete phone number
    if length<=10:
        return nan

    #find are code if has one
    else:
        if length==12:
            endIndx= 2
        else:
            endIndx=1
        areacode= normalizeNum[0:endIndx]
        return areacode


tidyTextTable()