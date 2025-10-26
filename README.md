## 🍔 Food E-commerce API (Django REST Framework)

**Tech Stack:** Python, Django, Django REST Framework, JWT Authentication, SQLite, Pillow, Django Filter

### Description
Developed a full-featured **Food E-commerce RESTful API** to manage the complete online food ordering process — including user registration, authentication, product management, cart, checkout, payment, and review systems. Designed using **modular Django apps** for scalability and clean architecture.

### 🔑 Key Features
- **User Authentication:** Secure user registration and login with JWT-based authentication (access & refresh tokens).  
- **Product Management:** CRUD APIs for food items with categories, availability, and price management.  
- **Cart & Checkout:** Separate cart and checkout apps supporting add/remove items, quantity updates, and total price calculation.  
- **Payment Integration:** Payment API for handling transactions with SSLCommerz.  
- **Order Management:** Endpoints for order placement, order history, and status tracking.  
- **Reviews & Ratings:** Customers can post reviews and give 1–5 star ratings for food items.  
- **Email Verification & Password Reset:** Implemented secure email-based verification and password reset, changes workflows.  
- **Filtering & Pagination:** Integrated django-filter and DRF pagination for efficient data retrieval. 


## Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/jahidul17/FoodEcommerce
    cd FoodEcommerce
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```


4. **Create a superuser (As admin login -Optional)**
    ```bash
    python manage.py createsuperuser
    ```


5. **Create .env file:**

    ```bash
    EMAIL=Your_email
    EMAIL_PASSWORD=From_goole_account_generated_app_password_not_email_password
    SECRET_KEY=your_secret_key
    DEBUG=True

    ```

5. **Apply migrations**
    ```bash
    python manage.py migrate
    ```

6. **Run the server**
    ```bash
    python manage.py runserver
    ```

7. **Access the project:**
    Open your browser and go to `http://127.0.0.1:8000/`<br>

---

