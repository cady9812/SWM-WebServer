from app import create_app

if __name__=="__main__":
    run_app = create_app()
    run_app.run(host="0.0.0.0", debug=True)

#######################################
####실행 방법 
######################################
# 이 파일을 만들고 python run.py 하거나
# 이 파일 지우고 flask run --host 0.0.0.0