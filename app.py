from flask import Flask, request, redirect, url_for, render_template, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import update, func
import os
import uuid



app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MPCC.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), unique=True, nullable=False)
    password = db.Column(db.String(1000), unique=True, nullable=False)


class Bill(db.Model):
    SNo = db.Column(db.Integer)
    Date = db.Column(db.Date, nullable=False)
    Project = db.Column(db.String(1000), nullable=False)
    SubContracter = db.Column(db.String(1000), nullable=False)
    VendorName = db.Column(db.String(1000), nullable=False)
    BillNo = db.Column(db.String(1000), nullable=False)
    ItemDiscription = db.Column(db.String(10000), nullable=False)
    SubItem = db.Column(db.String(10000), nullable=False)
    BillAmount = db.Column(db.String(1000), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False, default=0)
    PreviousQty = db.Column(db.Integer, nullable=False, default=0)
    Location = db.Column(db.String(1000), nullable=False)
    SubLocation = db.Column(db.String(1000), nullable=False)
    BOQItemNumber = db.Column(db.String(1000), nullable=False)
    BillCode = db.Column(db.String(1000), primary_key=True)
    PDFFilePath = db.Column(db.String(1000))
    ExcelFilePath = db.Column(db.String(1000)) 

    def __repr__(self):
        return f"{self.SNo} - {self.BillCode}"


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.Id
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256')
        try:
            new_user = Users(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except:
            flash(
                'Username already exists. Please choose a different username.', 'danger')
    return render_template('register.html')


@app.route('/index', methods=['GET', 'POST'])
def dashboard():
    bills = Bill.query.all()
    if 'username' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))
    return render_template('index.html', bills=bills)



@app.route('/add_search', methods=['GET', 'POST'])
def add_search():
    if str(request.form.get('search')) == 'true':
        base_query = Bill.query
        if request.form.get('date'):
            base_query = base_query.filter(
                Bill.Date == request.form.get('date'))
        if request.form.get('Project'):
            base_query = base_query.filter(
                Bill.Project == request.form.get('Project'))
        if request.form.get('SubContracter'):
            base_query = base_query.filter(
                Bill.SubContracter == request.form.get('SubContracter'))
        if request.form.get('vendorName'):
            base_query = base_query.filter(
                Bill.VendorName == request.form.get('vendorName'))
        if request.form.get('billNo'):
            base_query = base_query.filter(
                Bill.BillNo == request.form.get('billNo'))
        if request.form.get('ItemDifaddscription'):
            base_query = base_query.filter(
                Bill.ItemDiscription == request.form.get('ItemDiscription'))
        if request.form.get('SubItem'):
            base_query = base_query.filter(
                Bill.SubItem == request.form.get('SubItem'))
        if request.form.get('billAmount'):
            base_query = base_query.filter(
                Bill.BillAmount == request.form.get('billAmount'))
        if request.form.get('Quantity'):
            base_query = base_query.filter(
                Bill.Quantity == request.form.get('Quantity'))
        if request.form.get('Location'):
            base_query = base_query.filter(
                Bill.Location == request.form.get('Location'))
        if request.form.get('SubLocation'):
            base_query = base_query.filter(
                Bill.SubLocation == request.form.get('SubLocation'))
        if request.form.get('BOQItemNumber'):
            base_query = base_query.filter(
                Bill.BOQItemNumber == request.form.get('BOQItemNumber'))
        if request.form.get('billCode'):
            base_query = base_query.filter(
                Bill.BillCode == request.form.get('billCode'))
        # Execute the query to get the search results
        results = base_query.all()
        # Prepare the search results for rendering
        search_results = []
        for user in results:
            search_results.append({
                'SNo': user.SNo,
                'Date': user.Date,
                'Project': user.Project,
                'SubContracter': user.SubContracter,
                'VendorName': user.VendorName,
                'BillNo': user.BillNo,
                'ItemDiscription': user.ItemDiscription,
                'SubItem': user.SubItem,
                'BillAmount': user.BillAmount,
                'Quantity': user.Quantity,
                'PreviousQty': user.PreviousQty,
                'Location': user.Location,
                'SubLocation': user.SubLocation,
                'BOQItemNumber': user.BOQItemNumber,
                'BillCode': user.BillCode
            })
        return render_template('search.html', results=search_results)

    else:
        # Handle form submission functionality
        SNo = Bill.query.count() + 1
        bill_date = request.form.get('date')
        Project = request.form.get('Project')
        SubContracter = request.form.get('SubContracter')
        vendorName = request.form.get('vendorName')
        billNo = request.form.get('billNo')
        ItemDiscription = request.form.get('ItemDiscription')
        SubItem = request.form.get('SubItem')
        billAmount = request.form.get('billAmount')
        Quantity = request.form.get('Quantity')
        Location = request.form.get('Location')
        SubLocation = request.form.get('SubLocation')
        BOQItemNumber = request.form.get('BOQItemNumber')
        pdf_file = request.files['pdf_file']
        excel_file = request.files['excel_file']
        max_file_size = 1 * 1024 * 1024  # 1MB limit
        if pdf_file and pdf_file.content_length > max_file_size:
            flash('PDF file size exceeds the limit (1MB).', 'danger')
            return redirect(url_for('add_search'))

        if excel_file and excel_file.content_length > max_file_size:
            flash('Excel file size exceeds the limit (1MB).', 'danger')
            return redirect(url_for('add_search'))

        # Save the uploaded files to a designated folder (create the folder if it doesn't exist)
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)

        pdf_filename = str(uuid.uuid4()) + "_pdf.pdf"
        excel_filename = str(uuid.uuid4()) + "_excel.xlsx"

        pdf_file.save(os.path.join(upload_folder, pdf_filename))
        excel_file.save(os.path.join(upload_folder, excel_filename))
        billCode = request.form.get('billCode')        
        new_bill = Bill(
            SNo=SNo,
            Date=datetime.strptime(bill_date, '%Y-%m-%d').date(),
            Project=Project,
            SubContracter=SubContracter,
            VendorName=vendorName,
            ItemDiscription=ItemDiscription,
            BillNo=billNo,
            SubItem=SubItem,
            BillAmount=billAmount,
            Quantity=Quantity,
            Location=Location,
            SubLocation=SubLocation,
            BOQItemNumber=BOQItemNumber,
            PDFFilePath=os.path.join(upload_folder, pdf_filename),
            ExcelFilePath=os.path.join(upload_folder, excel_filename),
            BillCode=billCode
        )
        results = Bill.query.filter(
            Bill.BillCode.ilike(billCode)
        ).all()
        if results:
            print(Bill.BillNo)
            stmt = (
                update(Bill)
                .where(Bill.BillCode.ilike(billCode))
                .values(
                    PreviousQty=Bill.PreviousQty + Quantity,
                    Date=datetime.strptime(bill_date, '%Y-%m-%d').date(),
                    BillNo=billNo
                    # Append the new value to the existing BillNo
                    # BillNo=billNo
                )
            )
            db.session.execute(stmt)
        else:
            db.session.add(new_bill)
        db.session.commit()
        # flash('Bill added successfully!', 'success')
        return render_template('index.html') 

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_file(os.path.join("uploads", filename), as_attachment=True)

@app.route('/download_excel/<filename>')
def download_excel(filename):
    return send_file(os.path.join("uploads", filename), as_attachment=True)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
