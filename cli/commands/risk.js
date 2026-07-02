const axios = require('axios');

module.exports = async function (district) {
  try {
    const res = await axios.get(`http://127.0.0.1:5000/hello`);
    console.log(res.data.message);
  } catch (err) {
    console.log('Could not reach the crime API. Is it running?');
  }
};