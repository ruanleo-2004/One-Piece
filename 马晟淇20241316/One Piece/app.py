from applications import create_app

app = create_app()


if __name__ == '__main__':
    # 如果需要让局域网内其他设备访问，可以将host改为0.0.0.0
    app.run(host='127.0.0.1', port=5000, debug=True)
