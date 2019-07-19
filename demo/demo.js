const express = require('express');
const app = express();

app.set('view engine', 'hbs');
const path = require('path');
app.use(express.urlencoded({ extended: false }));

app.get("/",(req,res)=>{
  res.render("main",{})
});

app.listen(3000);
