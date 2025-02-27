from fastapi import FastAPI, HTTPException
from mangum import Mangum

from .environments import Environments

from .enums.transaction_type_enum import TransactionTypeEnum

from .entities.transaction import Transaction

app = FastAPI()

user_repo = Environments.get_user_repo()
transaction_repo = Environments.get_transaction_repo()

in_use_id = 1
factor = 2


@app.get("/")
def get_user():
    user = user_repo.get_user(user_id=in_use_id)

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    return user.to_dict()


@app.post("/deposit")
def deposit(request: dict):
    model = {
        "2": 0,
        "5": 0,
        "10": 0,
        "20": 0,
        "50": 0,
        "100": 0,
        "200": 0
    }

    transaction_value = 0.0

    for key in request:
        if model.get(key, None) is not None:
            transaction_value += int(key) * float(request[key])

    user = user_repo.get_user(user_id=in_use_id)

    if transaction_value >= user.current_balance * factor:
        raise HTTPException(status_code=403, detail="Depósito suspeito")

    user.current_balance += transaction_value

    transaction = Transaction(type=TransactionTypeEnum.DEPOSIT,
                              value=transaction_value,
                              current_balance=user.current_balance,
                              timestamp=1001.0)

    transaction_repo.create_transaction(transaction_id=int((transaction.current_balance * transaction.value) / 1000),
                                        transaction=transaction)

    return {
        "current_balance": transaction.current_balance,
        "timestamp": transaction.timestamp
    }


@app.post("/withdraw")
def withdraw(request: dict):
    model = {
        "2": 0,
        "5": 0,
        "10": 0,
        "20": 0,
        "50": 0,
        "100": 0,
        "200": 0
    }

    transaction_value = 0.0

    for key in request:
        if model.get(key, None) is not None:
            transaction_value += int(key) * float(request[key])

    user = user_repo.get_user(user_id=in_use_id)

    if transaction_value > user.current_balance:  #caso valor da transacao seja maior que o saldo do usuario
        raise HTTPException(status_code=403, detail="Saldo insuficiente para transação")

    user.current_balance -= transaction_value  #atualiza o saldo do usuario caso a transacao seja possivel

    transaction = Transaction(type=TransactionTypeEnum.WITHDRAW,
                              value=user.current_balance,
                              current_balance=user.current_balance,
                              timestamp=1001.0)

    transaction_repo.create_transaction(transaction_id=int((transaction.current_balance * transaction.value) / 1000),
                                        transaction=transaction)  #registrando uma nova transação com um ID específico no repositório de transações.

    return {
        "current_balance": transaction.current_balance,
        "timestamp": transaction.timestamp
    }


@app.get("/history")
def get_history(user_id: int = in_use_id):
    user = user_repo.get_user(user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    all_transactions = transaction_repo.get_all_transactions()

    transaction_history = []
    for transaction in all_transactions:
        transaction_history.append({
            "type": transaction.type.value,
            "value": transaction.value,
            "current_balance": transaction.current_balance,
            "timestamp": transaction.timestamp
        })

    return {"history": transaction_history}


handler = Mangum(app, lifespan="off")
