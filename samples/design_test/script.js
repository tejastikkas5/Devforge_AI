// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.btn-sm');
    const cartPanel = document.querySelector('.cart-panel');
    const cartItems = document.querySelector('.cart-items');
    const cartTotal = document.querySelector('.total');
    let total = 0;

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.card');
            const itemName = card.querySelector('h3').innerText;
            const itemPrice = parseFloat(card.querySelector('.price').innerText.replace('$', ''));
            total += itemPrice;

            const cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.innerHTML = `
                <div class="item-name">${itemName}</div>
                <div class="item-price">$${itemPrice.toFixed(2)}</div>
            `;
            cartItems.appendChild(cartItem);

            cartTotal.innerText = `$${total.toFixed(2)}`;
            cartPanel.style.display = 'block';
        });
    });

    // Close cart panel
    cartPanel.addEventListener('click', function(event) {
        if (event.target.classList.contains('cart-panel')) {
            cartPanel.style.display = 'none';
        }
    });
});
