import numpy as np

def split1d(Astart,Aend,Bstart,Bend):
    """For a 1-d pair of lines A and B:
    given start and end locations,
    produce new set of points for A, split by B.
    
    For example:
    split1d(1,9,3,5)
    splits the line from 1 to 9 into 3 pieces,
    1 to 3
    3 to 5
    and
    5 to 9
    it returns these three pairs and a list of whether
    those points were inside B.
    In this case the list is [False,True,False]
    """
    #five options
    #1 A and B don't intersect. This shouldn't happen
    if (Astart>=Bend) or (Bstart>=Aend):
        #Not sure what to do
        assert False
    #2 B starts first, and ends inside A:
    if (Astart>=Bstart) and (Bend<Aend):
        #return Astart-Bend Bend-Aend
        return [[Astart,Bend],[Bend,Aend]], [True, False]
    #3 B extends beyond limits of A in both directions:
    if (Bstart<=Astart) and (Bend>=Aend):
        #return A
        return [[Astart,Aend]], [True]
    #4 B starts in A and finishes after A
    if (Astart<Bstart) and (Bend>=Aend):
        #return Astart-Bstart Bstart-Aend
        return [[Astart,Bstart],[Bstart,Aend]], [False,True]
    #5 B is inside A
    if (Astart<Bstart) and (Bend<Aend):
        #return Astart-Bstart Bstart-Bend Bend-Aend
        return [[Astart,Bstart],[Bstart,Bend],[Bend,Aend]], [False,True,False]
    
def splitslice(Astart,Aend,Bstart,Bend,d):
    """given start and end locations, produce new set of points for A split by B
    just in dimension d."""
    chunks, inside = split1d(Astart[d],Aend[d],Bstart[d],Bend[d])
    res = []
    for chunk in chunks:
        newstart = Astart.copy()
        newend = Aend.copy()
        newstart[d] = chunk[0]
        newend[d] = chunk[1]
        res.append([newstart,newend])
    res
    return res, inside

def split(Astart,Aend,Bstart,Bend):
    """Given a hypercuboid, with the starting corner at Astart
    and ending corner at Aend. We want to split this hypercuboid
    into smaller hypercuboids, such that the edges of hypercubiod
    B (defined by Bstart and Bend) do not intersect any of the
    new hypercuboid edges.
    
    For example: split a hypercube, A, that extends from [0,1] to [2,3]
    with another, B, that extends from [1,1],[2,2]:
    
    split([0,1],[2,3],[1,1],[3,2])
    
                           
    | ___                |               | ___c
    ||A  |               |  B___         ||a|_|
    ||___|   slice with  |  |___|  gives ||_|_|b
    |_______             |______         |_______
     0 1 2
    results in three cuboids at:
    a [[0, 1], [1, 3]]
    b [[1, 1], [2, 2]]
    c [[1, 2], [2, 3]]
    """
    
    splits = [[Astart,Aend]]
    
    for d in range(len(Astart)):
        newsplits = []
        insides = []
        for s in splits:
            #print(all(s[1]>Bstart) and all(Bend>s[0]))
            #print(all(a>b for a,b in zip(s[1],Bstart)) and all(a>b for a,b in zip(Bend,s[0])))
            #print("---")
            #if all(a>b for a,b in zip(s[1],Bstart)) and all(a>b for a,b in zip(Bend,s[0])):
            if all(s[1]>Bstart) and all(Bend>s[0]):
                splitslices, inside = splitslice(s[0],s[1],Bstart,Bend,d)
                newsplits.extend(splitslices)
                insides.extend(inside)
            else:
                newsplits.extend([s])
                insides.append(False)
        splits = newsplits
    return splits, insides

def sumovercuboids(inputB, inputpeakgradslist,d):
    """
    Given a list of hypercuboids (inputB) and their gradients (inputpeakgradslist), what are the integrals over
    the d dimension of them?
    
    For example:
    
    4   ______________
    3  |    | 4  |    |
    2  | 1  |____| 2  |
    1  |    | 3  |    |
    0  |____|____|____|
       0 1  2 3  4 5  6
   
    - integrating along the (0) x-axis has two results, one between 0 and 2 (2+6+4=12), one between 2 and 4 (2+8+4=14).
    - integrating along the (1) y-axis has three results:
            - one between 0 and 2 of 4
            - one between 2 and 4 of 8+6 = 12
            - one between 4 and 6 of 8
    
    Demonstrating this with the method.
     the inputB array is an array of arrays, each one of the smaller arrays has the start and end locations
     of the cuboid for each dimension, for example a 4d hypercube from the origin to location (2,2,2,2) would be:
     np.array([[0,2],[0,2],[0,2],[0,2]])
    below we describe our space with a series of rectangles (as drawn above):
    
    inputB = np.array([np.array([[0,2],[0,6]]),np.array([[4,6],[0,6]]),np.array([[2,4],[0,3]]),np.array([[2,4],[3,6]])])
    inputpeakgradslist = np.array([[1],[2],[3],[4]])
        
    seglist = sumovercuboids(inputB,inputpeakgradslist,0)
    
    If we integrate along dimension 0:
    [{'grad': 0, 'int': 12, 'patch': [array([0]), array([3])]},
     {'grad': 0, 'int': 14, 'patch': [array([3]), array([6])]}]
 
    If we integrate along dimension 1, then we have three results
    [{'grad': 0, 'int': 6, 'patch': [array([0]), array([2])]},
     {'grad': 0, 'int': 21, 'patch': [array([2]), array([4])]},
     {'grad': 0, 'int': 12, 'patch': [array([4]), array([6])]}]
    
    
    A more complex example:
        inputB = np.array([np.array([[0,6],[0,4],[0,1]]),np.array([[0,2],[0,4],[1,3]]),np.array([[0,2],[0,4],[3,4]]),
                  np.array([[2,6],[0,4],[1,2]]),np.array([[2,4],[0,4],[2,4]]),np.array([[4,6],[0,2],[2,4]]),
                   np.array([[4,6],[2,4],[2,4]])])
        inputpeakgradslist = np.array([[2],[3],[1],[4],[2],[3],[5]])
        
        [{'grad': 0, 'int': 12, 'patch': [array([0, 0]), array([4, 1])]},
         {'grad': 0, 'int': 22, 'patch': [array([0, 1]), array([4, 2])]},
         {'grad': 0, 'int': 16, 'patch': [array([0, 2]), array([2, 3])]},
         {'grad': 0, 'int': 20, 'patch': [array([2, 2]), array([4, 3])]},
         {'grad': 0, 'int': 12, 'patch': [array([0, 3]), array([2, 4])]},
         {'grad': 0, 'int': 16, 'patch': [array([2, 3]), array([4, 4])]}]
    """
    
    #swap dimensions so we use the dimension specified as dimension zero - to make following code easier
    #(we always then integrate along the zeroth dimension)
    permutedB = inputB.copy() #make a copy so we don't screw up the copy given to us.
    temp = permutedB[:,d,:].copy()
    permutedB[:,d,:] = permutedB[:,0,:]
    permutedB[:,0,:] = temp
    
    #we need to add a final infinitely thin cuboid at the end
    #of the dimension we're summing over to tally up all the
    #results. This final cuboid has a gradient of zero, although
    #this doesn't really matter.
    outerbox = []
    for dim in range(permutedB.shape[1]):
        outerbox.append([np.min(permutedB[:,dim,0]),np.max(permutedB[:,dim,1])])
    outerbox = np.array(outerbox)
    Bendcuboid = outerbox.copy()
    Bendcuboid[0,:] = Bendcuboid[0,-1]
    B = np.r_[permutedB,[Bendcuboid]]
    peakgradslist = np.r_[inputpeakgradslist,np.array([[0]])]
    initialpatch = np.delete(outerbox,0,0).T
    seglist = []
    seglist.append({'patch':initialpatch,'grad':0,'int':0})
    laststart = 0
    orderbystart = np.argsort([b[0,0] for b in B])
    for b,p in zip(B[orderbystart],peakgradslist[orderbystart,0]):
        newlist = []
        for segdata in seglist:
            seg = segdata['patch']
            oldint = segdata['int']
            oldgrad = segdata['grad']
            delta = b[0,0]-laststart
            newint = oldint+delta*oldgrad
            newsegs, insides = split(seg[0],seg[1],b[1:,0],b[1:,1])
            for s,inside in zip(newsegs,insides):
                if inside:
                    grad = p
                else:
                    grad = oldgrad
                newlist.append({'patch':s,'grad':grad,'int':newint})
        laststart = b[0,0]
        seglist = newlist
    return seglist
