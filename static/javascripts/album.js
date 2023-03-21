function clicked_img(img,msg,fp){
          console.log(img.src);
          var top=document.getElementById('top')
          top.src = img.src;
          top.hidden=false;
          console.log(screen.width)
          top.width=img.naturalHeight;
          top.height=img.naturalWidth;
          console.log(msg);
          document.getElementById('msg').hidden = false;
          document.getElementById('msg').innerHTML="<h1>"+msg+"</h1>";
          document.getElementById('close').hidden = false;
 }


function do_close(){
  document.getElementById('top').hidden=true;
  document.getElementById('msg').hidden=true;
  document.getElementById('close').hidden=true;
}
