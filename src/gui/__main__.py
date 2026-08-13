import os
import sys
from importlib import resources 

def workdir():  #pysca использует механизм entry-points для запуска проекта, надо только знать где data
    return resources.files( sys.modules[__name__] ).joinpath("data")

#запуск проекта cli-утилитой pysca.cli
def main():
    from pysca.cli.project import app
    if (workdir() / "project.yaml").is_file():
        os.environ['PREFIX']='src/gui/data/'
        os.environ['PYSCAWORKDIR'] = str(workdir())
    else:
        os.environ['PYSCAWORKDIR'] = str(resources.files("gui") / ".." / "..")
    app()
    
if __name__=="__main__":
    sys.argv +=["run"]
    main()