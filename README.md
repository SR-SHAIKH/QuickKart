QuickKart

QuickKart is a hyperlocal quick commerce web application built with Django and PostgreSQL. It enables customers to discover and order products from local shops, while shop owners and delivery riders manage their business and deliveries efficiently. The platform is designed for speed, reliability, and a seamless user experience across devices.

---

🚀 Features
**Multi-role System:** Customer, Shop Owner, and Rider registration and dashboards
**Product Search & Filtering:** Find products by name, category, or shop
**Cart & Wishlist:** Add products to cart or wishlist for easy shopping
**Order Management:** Place, track, and manage orders with real-time status updates
**OTP-based Registration & Login:** Secure authentication using email OTP
**Payment Integration:** Cashfree payment gateway for secure online payments
**Shop & Product Management:** Shop owners can add/edit products, manage orders, and view analytics
**Responsive UI:** Mobile-first design using Bootstrap 5 and Tailwind CSS
**Admin Dashboard:** Django admin for superuser management
**PDF Invoice Generation:** Downloadable invoices for every order
**Pincode-based Shop Discovery:** Customers see only shops/products in their area
**AJAX-powered Cart & Wishlist:** Smooth, no-page-reload experience


🛠️ Technology Stack
**Backend:** Python 3, Django
**Database:** PostgreSQL
**Frontend:** Bootstrap 5, Tailwind CSS, HTML5, JavaScript (AJAX)
**Payments:** Cashfree API
**Deployment:** Render.com
**Other:** Django ORM, Django Templates, Custom User Model


⚙️ Setup Instructions

1. **Clone the repository:**
   git clone https://github.com/SR-SHAIKH/QuickKart
   cd quickkart
   

2. **Create a virtual environment and activate it:**

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   

3. **Install dependencies:**
   pip install -r requirements.txt
   

4. **Configure environment variables:**
   - Create a `.env` file or set environment variables for database, email, and payment gateway credentials as needed.

5. **Apply migrations:**
   python manage.py migrate
   

6. **Create a superuser (for admin access):** 
   python manage.py createsuperuser


7. **Run the development server:**  
   python manage.py runserver


8. **Access the app:**
   -Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.



📁 Folder Structure


FYproject/
├── localshop/           # Django project settings
├── shop/                # Main Django app (models, views, templates, forms)
│   ├── templates/
│   ├── static/
│   ├── forms.py
│   ├── models.py
│   └── views.py
├── users/               # Custom user app
├── media/               # Uploaded files
├── static/              # Static assets (CSS, JS, images)
├── requirements.txt     # Python dependencies
├── manage.py            # Django management script
└── README.md            # Project documentation


---

👤 User Roles
**Customer:** Browse, search, and order products. Manage cart, wishlist, and orders.
**Shop Owner:** Register shop, add/edit products, manage orders, view analytics.
**Rider:** Register, view assigned deliveries, update delivery status.
**Admin:** Full control via Django admin panel.


📝 Contribution Guidelines
1. Fork the repository and create your branch:   
   git checkout -b feature/your-feature-name
   
2. Make your changes and commit:  
   git commit -m "Add your message here"
   
3. Push to your fork and submit a pull request.
4. For major changes, open an issue first to discuss what you would like to change.


📄 License
This project is licensed under the [MIT License](LICENSE).


📬 Contact
For any queries, suggestions, or support, contact:
**Email:** your.email@example.com
**GitHub:** [yourusername](https://github.com/yourusername)


**Happy Shopping with QuickKart!** 🚚🛒 
