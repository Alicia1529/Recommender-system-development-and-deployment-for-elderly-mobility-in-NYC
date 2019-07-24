

function showRadius(){
    const value = document.getElementById("radius").value;
    document.getElementById("show-radius").innerText = value;
}

function addZero(i) {
    if (i < 10) {
      i = "0" + i;
    }
    return i;
  }
function like(event,user_id,restaurant_id){

  const date = new Date()
  const time = addZero(date.getHours())+":"+addZero(date.getMinutes())
  var url = `http://localhost:8000/feedback:${user_id}+${time}+${restaurant_id}+1`

  fetch(url,{mode: 'cors',headers:{'Access-Control-Allow-Origin':'*' }})
    .then(function(response){
    })
    .catch(error => console.log('Error:', error));
}
function disLike(event,user_id,restaurant_id){
  const date = new Date()
  const time = addZero(date.getHours())+":"+addZero(date.getMinutes())
  var url = `http://localhost:8000/feedback:${user_id}+${time}+${restaurant_id}+0`

  fetch(url,{method:"GET",mode:'cors',headers:{'Access-Control-Allow-Origin':'*' }})
    .then(function(response){
    })
    .catch(error => console.log('Error:', error));
}

function updateElement(node,index,info){
  const user_id = document.getElementById("user_id").value;

  node.setAttribute("value",info.id)
  node.setAttribute("class","recommendation-result");
  node.setAttribute("id","recommendation_num_"+index);
  
  category = info.categories.map(x=>x["title"]).join("・");
  distance = Math.round(info.distance)
  text = `<span style='font-size:1.025em'>${info.name}&nbsp</span><span style='font-size:0.75em'>(${distance} m)</span><br>\
          <span style='font-size:1em'>${info.rating}🌟・${info.review_count} reviews・${info.price}</span><br>\
          <span style='font-size:0.75em'>${category}</span><br>\
          <span style='font-size:1em'>${info.location}</span><br>\
          <span style='margin-left:12%'><button name="call">Call</button><button name="go">Go</button><button name="dislike">No interest</button></span>`
  node.innerHTML = text;
  const call = document.querySelector(`#recommendation_num_${index} button[name="call"] `);
  const go = document.querySelector(`#recommendation_num_${index} button[name="go"] `);
  const dislike = document.querySelector(`#recommendation_num_${index} button[name="dislike"]`);
  call.addEventListener("click",(event)=>{like(event,user_id,info.id)})
  go.addEventListener("click",(event)=>{like(event,user_id,info.id)})
  dislike.addEventListener("click",(event)=>{disLike(event,user_id,info.id)})
  
  return node
  
}


function getRecommendation(){
    const user_id = document.getElementById("user_id").value;
    const longitude = document.getElementById("longitude").value;
    const latitude = document.getElementById("latitude").value;
    const radius = document.getElementById("radius").value;
    const price = document.getElementById("price").value;
    const date = new Date()
    const time = addZero(date.getHours())+":"+addZero(date.getMinutes())

    var url = `http://localhost:8000/getRecommendation:${user_id}+${time}+${longitude}+${latitude}+${radius}+${price}`

    fetch(url,{method:"GET"})
      .then(function(response){
        if(response.status >= 200 && response.status < 300) {
          return response.json();
        }
        else{
          throw new Error('Fail to post questions');
        }
      })
      .then(function(data){
        console.log(data)
        const root = document.getElementById("recommendation-box");
        for (let i=0;i<3;i++){
          node = document.getElementById("recommendation_num_"+i);
          if (!node){
            node = document.createElement("div")
            root.appendChild(node);
            // node.addEventListener("click",)
          }
          updateElement(node,i,data[i]);
        }

      })
      .catch(error => console.log('Error:', error));

}

function main() {
    showRadius();
    const radiusInput = document.getElementById("radius");
    radiusInput.addEventListener("click",showRadius);
    const recommendation = document.getElementById("recommend");
    recommendation.addEventListener("click",getRecommendation);
  }
  
  document.addEventListener("DOMContentLoaded", main);