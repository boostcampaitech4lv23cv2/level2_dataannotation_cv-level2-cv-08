import clipboard

while True:
    # input
    code = input()

    # break condition
    if code == 'exit':
        break

    # encoding
    result = code.encode('ascii', 'backslashreplace')

    # decoding
    result = result.decode('utf-8')

    # copy
    print('Copy successfully!!: ' + result)
    clipboard.copy(result)