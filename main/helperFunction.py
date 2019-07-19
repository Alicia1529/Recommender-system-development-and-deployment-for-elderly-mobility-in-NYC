# A and b both have three matrices, one for morning, one for afternoon and one for evening
# if there is no matrcies stored, then start  with None
import pickle 
import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='UrbanConnectorTest',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)



def getMatrices(time):
    A = None
    b = None

    if time <= "10:30":
        try:
            A = pickle.load(open("model/A1.pyc","rb"))
            b = pickle.load(open("model/b1.pyc","rb"))
        except:
            pass
    elif time<= "14:00":
        try:
            A = pickle.load(open("model/A2.pyc","rb"))
            b = pickle.load(open("model/b2.pyc","rb"))
        except:
            pass
    else:
        try:
            A = pickle.load(open("model/A3.pyc","rb"))
            b = pickle.load(open("model/b3.pyc","rb"))
        except:
            pass
    return A,b



def saveMatrices(A, b, time):
    if time <= "10:30":
        pickle.dump(A,open("model/A1.pyc","wb"))
        pickle.dump(b,open("model/b1.pyc","wb"))

    elif time<= "14:00":
        pickle.dump(A,open("model/A2.pyc","wb"))
        pickle.dump(b,open("model/b2.pyc","wb"))

    else:
        pickle.dump(A,open("model/A3.pyc","wb"))
        pickle.dump(b,open("model/b3.pyc","wb"))


def periodicalUpdateDatabase(conn):
#delete recommendation made before 7 days
    query = "DELETE FROM Recommendation WHERE timestamp < (NOW() - INTERVAL 7 DAY)"
    conn.cursor().execute(query)
    conn.commit()
    
