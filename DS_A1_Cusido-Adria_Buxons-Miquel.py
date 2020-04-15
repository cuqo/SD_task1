import pywren_ibm_cloud as pywren
from cos_backend import COSBackend
import json
import io
import numpy
import random
import time

MAX_RANDOM = 10000
dim1 = 20
dim2 = 10
dim3 = 6
nWorkers = 180


def generateMatrix(name, pos,dimf ,dimc):
    numpy.random.seed()
    cos = COSBackend()
    
    #generate random matrix
    mat_original = numpy.random.randint(MAX_RANDOM, size=(dimf, dimc))
    
    #upload to cloud
    memfile = io.BytesIO()
    numpy.save(memfile, mat_original)
    memfile.seek(0)
    serialized = json.dumps(memfile.read().decode('latin-1'))

    cos.put_object('cuc-bucket', name, serialized)
    if pos is 'A':
        toRows(mat_original)
    else:
        toColumns(mat_original)



def toRows(mat):
    cos = COSBackend()
    #storage the rows of matrix A (AxB) to the bucket
    for x in range(0, dim1):
        row = mat[x,:]

        memfile = io.BytesIO()
        numpy.save(memfile, row)
        memfile.seek(0)
        serialized = json.dumps(memfile.read().decode('latin-1'))

        cos.put_object('cuc-bucket', 'A'+str(x), serialized)


def toColumns(mat):
    cos = COSBackend()
    #storage the columns of matrix B (AxB) to the bucket
    for x in range(0, dim3):
        column = mat[:,x]

        memfile = io.BytesIO()
        numpy.save(memfile, column)
        memfile.seek(0)
        serialized = json.dumps(memfile.read().decode('latin-1'))
        
        cos.put_object('cuc-bucket', 'B'+str(x), serialized)

def my_map_function(vec):    
    cos = COSBackend()
    resX = []

    vec = numpy.array(vec)

    for act in range(0, len(vec)):
        actual = vec[act]
        i = actual[0]
        j = actual[1]
        
        #load the row of the first matrix
        nameRow ='A'+str(i)
        serialized1 = cos.get_object('cuc-bucket', nameRow)
        memfile = io.BytesIO()
        memfile.write(json.loads(serialized1).encode('latin-1'))
        memfile.seek(0)
        row = numpy.load(memfile)

        #load the column of the second matrix
        nameColumn ='B'+str(j)
        serialized2 = cos.get_object('cuc-bucket', nameColumn)
        memfile = io.BytesIO()
        memfile.write(json.loads(serialized2).encode('latin-1'))
        memfile.seek(0)
        col = numpy.load(memfile)

        #calculation row * column
        x = numpy.dot(row,col)
        res = [x, i, j]
        resX.append(res)

    return resX

def my_reduce_function(results):
    cos = COSBackend()
    matrix = numpy.zeros((dim1,dim3))

    #generate final matrix from parcial results
    for xResult in results:
        for map_result in xResult:
            matrix[map_result[1],map_result[2]]=map_result[0]
    
    
    #put the fianl matrix to bucket
    memfile = io.BytesIO()
    numpy.save(memfile, matrix)
    memfile.seek(0)
    serialized = json.dumps(memfile.read().decode('latin-1'))

    cos.put_object('cuc-bucket', 'matriu_result', serialized)
    
    return matrix

def calculateWorkVector():
    dimGeneral = dim1 * dim3
    workAll = dimGeneral // nWorkers
    workOver = dimGeneral % nWorkers

    #calculate the number of chunks per worker
    ret = []
    for i in range(0,nWorkers):
        if workOver > 0:
            ret.append(workAll + 1)
            workOver = workOver - 1
        else:
            ret.append(workAll)
    
    ret = numpy.array(ret)
    
    #generate iterdata vector
    cont = 0
    tmp = ret[cont]
    aux = []
    aux2 = []
    iterdata = []
    for i in range(0,dim1):
        for j in range(0,dim3):
            pos = [i,j]
            aux.append(pos)
            if tmp == 1:
                aux2.append(aux)
                iterdata.append(aux2)
                aux = []
                aux2 = []
                cont = cont + 1
                tmp = ret[cont%len(ret)]
            else:
                tmp = tmp - 1 
    
    return iterdata

if __name__ == '__main__':
    if nWorkers > 100:
        nWorkers =100
        
    ibmcf = pywren.ibm_cf_executor()
    params = ['matriu1', 'A', dim1, dim2 ]
    ibmcf.call_async(generateMatrix, params)
    
    params = ['matriu2', 'B' , dim2 , dim3 ]
    ibmcf.call_async(generateMatrix, params)
    
    start_time = time.time()

    iterdata = calculateWorkVector()

    futures = ibmcf.map_reduce(my_map_function, iterdata, my_reduce_function)
    ibmcf.wait(futures)
    elapsed_time = time.time() - start_time
    print(ibmcf.get_result())
    print("Temps d'execucio: ", elapsed_time, ' seg')
    print("Matriu A: ", dim1,"X",dim2)
    print("Matriu B: ", dim2,"X",dim3)
    print("Matriu final:", dim1,"X",dim3)
    print("#Workers: ", len(iterdata))



