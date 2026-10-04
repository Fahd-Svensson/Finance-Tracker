from flask import Flask ,render_template , url_for , request , make_response , flash , redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import date , datetime
from sqlalchemy import func
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']  = False#this will be tracking notifications
app.config['SECRET_KEY']  = 'my-secret-key'#VERY IMPORTANT
db = SQLAlchemy(app)

class Expense(db.Model): #basically Model is what we get from the db instance
   #THIS IS CREATING THE DB TABLE
   id =db.Column(db.Integer , primary_key = True)
   description =db.Column(db.String(120) , nullable=False)
   amount =db.Column(db.Float , nullable=False)
   category =db.Column(db.String(120) , nullable=False)
   date =db.Column(db.Date , nullable=False , default =date.today)

with app.app_context():
    db.create_all()#Creating the datbase


CATEGORIES =['Food' , 'Transport' , 'Rent' , 'Utilities' , 'Health']




def parse_date_or_none(s: str): #whateever s will be it will come out as a string
   if not s:
      return None
   try:
      return datetime.strptime(s ,'%Y-%m-%d').date()
   except ValueError:
      return None
   






@app.route('/')
def index():
  #1 read query strings
    start_str = (request.args.get('start') or '').strip()
    end_str = (request.args.get('end') or '').strip()
    selected_category = (request.args.get('category') or '').strip()
   # parsing strings
    start_date = parse_date_or_none(start_str)
    end_date = parse_date_or_none((end_str))

    if start_date and end_date and end_date < start_date:
       flash('End date cannot be before start date' , 'error')
       start_date = end_date = None #resetting the date to none
       start_str = end_date ='' #and setting strings to empty strings

    q = Expense.query

    if start_date:
      q = q.filter(Expense.date >= start_date)
    if end_date:
      q = q.filter(Expense.date <= end_date)
    if selected_category:
       q = q.filter(Expense.category == selected_category)
    
    

    expenses = q.order_by(Expense.date.desc() , Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)
    print(expenses)



     #for the pichart
    cat_q = db.session.query(Expense.category, func.sum(Expense.amount))

    if start_date:
       cat_q = cat_q.filter(Expense.date >= start_date)
    if end_date :
        cat_q = cat_q.filter(Expense.date <= end_date)

    if selected_category :
        cat_q = cat_q.filter(Expense.category == selected_category)

    cat_row = cat_q.group_by(Expense.category).all()
    cat_labels = [c for c, _ in cat_row]
    cat_values = [round(float(s or 0),2) for _, s in cat_row]
    




   #for the day chart
    day_q = db.session.query(Expense.date, func.sum(Expense.amount))

    if start_date:
      day_q = day_q.filter(Expense.date >= start_date)
    if end_date :
      day_q = day_q.filter(Expense.date <= end_date)

    if selected_category :
      day_q = day_q.filter(Expense.category == selected_category)

    day_row = day_q.group_by(Expense.date).order_by(Expense.date).all()
    day_labels = [d.isoformat() for d, _ in day_row]
    day_values = [round(float(s or 0),2) for _, s in day_row]
    print(day_labels)
    


       










    return render_template(
       
       
       'index.html',
                           
                           
                           
                            expenses = expenses,
                            categories = CATEGORIES,
                            today = date.today().isoformat(),
                            total = total,
                            start_str = start_str,
                            end_str = end_str,
                            selected_category  = selected_category,
                            cat_labels = cat_labels,
                            cat_values = cat_values,
                             day_labels = day_labels,
                            day_values = day_values
                            )

@app.route('/add' , methods=['POST'])
def add():

   description = request.form.get(('description') or '').strip() #no strip you will end up getting none
   amount_str = request.form.get(('amount') or '').strip()
   category = request.form.get(('category') or '').strip()
   date_str = request.form.get(('date') or '').strip()

   if not description or not amount_str or not category:
      flash('Please fill description, amount, and category', 'error')
      redirect(url_for('index'))

   try:
      amount = float(amount_str)
      if amount <= 0 :
         raise ValueError

   except ValueError:
        flash('Amount must be a positive number' , 'error')
        return redirect(url_for('index'))

   try:
      d = datetime.strptime(date_str , '%Y-%m-%d').date() if date_str else date.today()

   except ValueError:
      d = date.today()


   e = Expense(description = description , amount = amount , category = category , date = d)
   db.session.add(e)
   db.session.commit()

   flash('Expense added', 'Success')
   return redirect(url_for('index'))


    
@app.route('/delete/<int:expense_id>' , methods = ['POST'])#so /delete is basically creating a route called route delete , and the tag is basically taking the tag id
def delete(expense_id):
   e = Expense.query.get_or_404(expense_id)
   db.session.delete(e)
   db.session.commit()
   flash('Expense deleted' , 'success')
   return redirect(url_for('index'))



if __name__  == '__main__':
  app.run(debug=True , port = 5000)