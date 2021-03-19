(window.onloadeddata = function (){
    
    document.querySelectorAll('.collapse-action').forEach(function(e){
        e.addEventListener('click', function() {
            document.querySelector(this.getAttribute('data-collapse-target'))
            .classList.toggle('collapsable--collapsed');
        })
    })

})();