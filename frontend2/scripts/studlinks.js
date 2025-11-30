/*const cours = document.getElementsByTagName("a");
console.log(cours);
cont = document.getElementsByClassName("content");
cou = document.createElement('div');
cou.className += 'courses';
cours.addEventListener('click', (e)=> {
    e.preventDefault();
    cont = cont.appendChild(cou);
//});*/
let c = document.querySelector("a.c");
c.addEventListener('click', function(e){
    document.getElementById("chat").style.cssText = 'display: none;';
    document.getElementById("courses").style.cssText = 'display: flex;';
});
let ch = document.querySelector("a.ch");
ch.addEventListener('click', function(e){
    document.getElementById("courses").style.cssText = 'display: none;';
    document.getElementById("chat").style.cssText = 'display: flex;';
});