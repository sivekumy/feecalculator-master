from flask import Flask, render_template, request, flash, redirect, url_for
from forms import ContactForm
from flask_mail import Message, Mail

import sys
import pandas as pd
import numpy as np

from forex_python.converter import CurrencyRates

mail = Mail()

application = Flask(__name__)
application.secret_key = "SECRETKEY"

#Config mail for Feedback page 
application.config["MAIL_SERVER"] = "smtp.gmail.com"
application.config["MAIL_PORT"] = 465
application.config["MAIL_USE_SSL"] = True
application.config["MAIL_USERNAME"] = 'ysivekum@gmail.com'
application.config["MAIL_PASSWORD"] = 'ocsxjlfzgnqjrmyt'

mail.init_app(application)

#route for the Home page
@application.route("/")
def home():
    return render_template('home.html')

#route for the Upload page
@application.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        print(request.files['file'])
        f = request.files['file']
        currency = request.form['currency']
        download = request.form.getlist('download')
        display = request.form.getlist('display')
        
        #check if file was uploaded
        if f.filename == '':
            flash(u'Please upload a file', 'confirmation')
            return redirect(url_for('upload'))
        
        #check if file is correct file type (csv)
        if f.filename.rsplit('.', 1)[1].lower() != 'csv':
            flash(u'Please upload a csv file', 'confirmation')
            return redirect(url_for('upload'))

        #checks if user wants to download and/or display results in browser
        downloadCheck = bool(download)
        displayCheck = bool(display)
        
        #checks if both download and display were not selected
        if downloadCheck is False and displayCheck is False:
            flash(u'Please select at least one: Download or Display in Browser', 'confirmation')
            return redirect(url_for('upload'))

        data_xls = pd.read_csv(f)
        
        trans_ordervalue = 0    #initialize transaction fee variable
        trans_shipping = 0      #initialize shipping fee variable
        order_net_updated = 0   #initialize net order value variable
        
        c = CurrencyRates()
        rate = c.get_rate('USD', currency) #get exchange rate of selected currency to USD
        listing_fee = round(rate*0.20, 2)
        
        trans1 = []            #stores transaction fees for all orders
        trans2 = []            #stores shopping fees for all orders
        orderNetUpdated = []   #stores net order values for all orders
        listingfees =[]        #stores listing fees for all orders
        
        #Calculates fees for each order in file
        for index, row in data_xls.iterrows():
            trans_ordervalue = row['Order Value']*0.05    #5% transaction fee 
            trans_shipping = row['Delivery']*0.05         #5% shipping fee
            
            #update total value after taking into account all the fees
            order_net_updated = float(row['Order Value']) + float(row['Delivery']) - float(row['Discount Amount']) - float(row['Delivery Discount']) - float(row['Card Processing Fees']) - trans_ordervalue - trans_shipping - listing_fee
            trans1.append('%.2f' % round(trans_ordervalue,2))
            trans2.append('%.2f' % round(trans_shipping,2))
            orderNetUpdated.append('%.2f' % round(order_net_updated, 2))
            listingfees.append('%.2f' % listing_fee)
        
        #Creates 4 new columns in csv file and populates with the appropriate arrays
        data_xls['Transaction Fee'] = trans1
        data_xls['Shipping Transaction Fee'] = trans2
        data_xls['Listing Fee'] = listingfees
        data_xls['Order Net Updated'] = orderNetUpdated
        
        #Replace n/a with blanks
        data_xls = data_xls.replace(np.nan, '', regex=True)
        
        #display results and download updated file
        if downloadCheck is True and displayCheck is True:
            data_xls.to_csv('output.xlsx', index = False, header = True)
            flash(u'Download Complete!', 'confirmation')
            return render_template('table.html', tables=[data_xls.to_html(classes='data')], titles= data_xls.columns.values)

        #download updated file only
        if downloadCheck is True:
            data_xls.to_csv('output.xlsx', index = False, header = True)
            flash(u'Download Complete!', 'confirmation')
            return redirect(url_for('upload'))
        
        #display results in browserr only
        if displayCheck is True:
            return render_template('table.html', tables=[data_xls.to_html(classes='data')], titles= data_xls.columns.values)
        
    return render_template('upload.html')

#Route for the Feedback page
@application.route("/feedback",methods=['GET', 'POST'])
def feedback():
    form = ContactForm(request.form)
        
    if request.method == 'POST':
        #check if there are any errors in the input
        if form.validate() is False:
            return render_template('feedback.html', form=form)
        else:
            flash(u'Feedback Received. Thank you!', 'confirmation')
            #format email
            msg = Message(form.subject.data, sender='contact@example.com', recipients=['ysivekum@gmail.com'])
            msg.body = """
            From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            form.name.data = ""
            form.email.data = ""
            form.subject.data = ""
            form.message.data = ""
            return render_template('feedback.html', form = form)
    
    elif request.method == 'GET':
        return render_template('feedback.html', form=form)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
