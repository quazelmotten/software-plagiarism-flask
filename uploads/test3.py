def biggest_2d_non_cubic_cube():
    list1=[]
    list2=[]
    for i in range(n):
        for j in range(i, n):
            for k in range(j,n):
                if points[i][0]==points[j][0] and points[i][1]==points[k][1]:
                    x1=points[k][0]
                    y1=points[j][1]
                    if (x1,y1) in points:
                        d=dist3(points[i], points[j], points[k])
                        list1=[points[i], points[j], points[k], (x1,y1), d]
                        list2.append(list1)
    list2=sorted(list2, key=lambda x:x[-1], reverse=True)
    print(list2[0])
def biggest_2d_cube():
    list1=[]
    list2=[]
    for i in range(n):
        for j in range(i, n):
            for k in range(j,n):
                if points[i][0]==points[j][0] and points[i][1]==points[k][1] and dist2(points[i], points[j])==dist2(points[i], points[k]):
                    x1=points[k][0]
                    y1=points[j][1]
                    if (x1,y1) in points:
                        d=dist3(points[i], points[j], points[k])
                        list1=[points[i], points[j], points[k], (x1,y1), d]
                        list2.append(list1)
    list2=sorted(list2, key=lambda x:x[-1], reverse=True)
    if list2[0][-1]==0:
        print('No square.')
    else:
        print(list2[0])

def main():
    n=int(input())

    points=[]

    for i in range(n):

        x=int(input())

        y=int(input())

        points.append((x,y))

    biggest_2d_non_cubic_cube()

    biggest_2d_cube()

if __name__ == '__main__':
    main()
