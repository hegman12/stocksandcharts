 margin = {
     top: 30,
     bottom: 30,
     left: 50,
     right: 30
 }

 var svg1Width = d3.select('#graphOne').style("width").replace("px", "");
 var svg1Height = d3.select('#graphOne').style("height").replace("px", "");
 var svg2Width = d3.select('#graphTwo').style("width").replace("px", "");
 var svg2Height = d3.select('#graphTwo').style("height").replace("px", "");
 var graphOne = d3.select('#graphOne').append("g").attr("height", svg1Height - margin.top - margin.bottom).attr("width", svg1Width - margin.left - margin.right).attr("transform", "translate(" + margin.left + "," + margin.top + ")").attr("fill", "black");
 var graphTow = d3.select('#graphTwo').append("g").attr("height", svg2Height - margin.top - margin.bottom).attr("width", svg2Width - margin.left - margin.right).attr("transform", "translate(" + margin.left + "," + margin.top + ")");
 var primaryStockID = null
 var secondaryStockID = null
 var resultCatId = null
 var resultTypeId = null
 var totalQtr = 20;
 var getPrice1 = false
 var getPrice2 = false
 var stockPrice1 = null;
 var stockPrice2 = null;

 function getRandom(min, max) {
     return Math.floor(Math.random() * (max - min) + min);
 };

 function scale(n, max, min = 1) {
     return Math.floor((n - min) / (max - min));
 }

 function getMax(data) {
     max = 0;
     for (i = 0; i < data.length; i++) {
         if (data[i].value > max) {
             max = data[i].value;
         }
     }
     return max;
 }

 function getMin(data) {
     min = 9999999999999;
     for (i = 0; i < data.length; i++) {
         if (data[i].value < min) {
             min = data[i].value;
         }
     }
     return min;
 }

 function getNames(data) {
     names = []
     for (i = 0; i < data.length; i++) {
         names[i] = data[i].year
     }
     return names;
 }

 function getSearchResults(id, lbl, type) {
     var searchString = document.getElementById(lbl).value
     if (searchString.length > 2) {
         var url = "/search/" + searchString
         d3.json(url, {
             headers: {
                 "Authorization": "Basic " + token
             }
         }).then(function(data) {
             updateSearchResults(data, "#" + id, type)
         }).catch(function(error) {
             console.log(error)
             if (error) {
                 window.location.href = "/"
             }
         })
     } else {
         clearSearchResults("#" + id);
     }
 }

 function updateSearchResults(data, id, type) {
     d3.select(id).attr("class", "enabled");
     var updates = d3.selectAll(id).selectAll("label").data(data, function(d) {
         return parseInt(d.stockId);
     });

     updates.exit().remove();
     updates.enter().append("label").order().attr("class", "dropdown-items").html(function(d) {
         return d.stockName
     }).attr("tabIndex", "0").on("click", function(d) {
         if (type == 'p') {
             primaryStockClick(d);
             d3.selectAll(id).selectAll("label").remove();
             d3.select(id).attr("class", "disabled");
             d3.selectAll(".options").style("visibility", "visible");
             resetOptions();
             clearCategory();
             clearType();
             hideGraphPanel();
             getPrice1 = true;
             //getResultCategory("#resultCategory", primaryStockID);
         } else {
             secondaryStockClick(d);
             getPrice2 = true;
             d3.selectAll(id).selectAll("label").remove();
             d3.select(id).attr("class", "disabled");
             if (totalQtr != null) {
                 getResultCategory("#resultCategory", primaryStockID);
             }
         }
     });
 }

 function updatePrimaryStockName(name) {
     d3.select("#companyLabel").html(name);
     d3.select("#companyName").property("value", "");
     d3.select("#companyName").attr("placeholder", "Search stocks");
     d3.selectAll("head title").html(name);
 }

 function primaryStockClick(data) {
     updatePrimaryStockName(data.stockName);
     primaryStockID = data.stockId;
 }

 function secondaryStockClick(d) {
     d3.select("#compareLabel").html(d.stockName);
     d3.select("#companyCompare").property("value", "");
     d3.select("#companyCompare").attr("placeholder", "Search another stock");
     secondaryStockID = d.stockId;
 }

 function clearSearchResults(id) {
     var removeItems = d3.selectAll(id).selectAll("label").data([], function(d) {
         return "div" + d.value;
     })
     removeItems.exit().remove();
     d3.select(id).attr("class", "disabled");
 }


 function toggleCheckBox(id) {
     var checked = document.getElementById(id).checked;
     if (checked == true) {
         d3.selectAll(".cinput .enabled").attr("class", "disabled");
         secondaryStockID = null
         d3.select("#compareLabel").html("");
         d3.select("#companyCompare").attr("placeholder", "Search another stock");
         d3.selectAll(".cinput .enabled").property("checked", false);
         d3.selectAll("#g2").style("visibility", "hidden");
         getResultCategory("#resultCategory", primaryStockID);
     } else {
         d3.selectAll(".cinput .disabled").attr("class", "enabled");
         d3.selectAll(".cinput .enabled").property("checked", true);
         //getResultCategory("#resultCategory", primaryStockID);
     }
 };

 function toggleqryrLabels(id) {
     d3.selectAll("#noOfQtr label").style("background", "");
     //d3.select(id).classed("tagSelected", true);
     d3.select(id).style("background", "rgba(104, 190, 243, 1)");
     if (id == "#qrid2") {
         totalQtr = 8;
     } else if (id == "#qrid3") {
         totalQtr = 12;
     } else if (id == "#qrid1") {
         totalQtr = 6;
     } else {
         totalQtr = 20;
     }
     getResultCategory("#resultCategory", primaryStockID);
 };

 function getResultCategory(id, stockID) {
     var end_url = "/" + totalQtr
     console.log(totalQtr)
     var singleCompare = document.getElementById('singleCompare').checked
     var mode = ''
     if (singleCompare == true && secondaryStockID != null) {
         mode = 'C';
         end_url = end_url + "?stockCompare=" + secondaryStockID;
     } else {
         mode = 'S';
     }
     var url = "/category/" + stockID + "/" + mode + end_url;
     //var url = "/category/3266" + "/" + mode + end_url;
     d3.json(url, {
         headers: {
             "Authorization": "Basic " + token
         }
     }).then(function(data) {
         updateResultCategory(id, data)
     }).catch(function(error) {
         if (error) {
             //window.location.href = "/"
         }
     })
 }

 function updateResultCategory(id, data) {
     d3.selectAll("#resultCategory div label").classed("tagSelected", false);
     d3.selectAll(id).style("visibility", "visible");
     //d3.selectAll("#resultType").style("visibility", "visible");
     resultCatId = null
     d3.selectAll(".graphPanel").style("visibility", "hidden");
     d3.selectAll("#resultType").style("visibility", "hidden");
     var tags = d3.selectAll(id).selectAll("div").data(data, function(d) {
         return "catdiv" + d.label_id;
     })
     tags.exit().remove()
     tags.enter().append('div').attr("class", "tag").attr("id", function(d) {
             return "catdiv" + d.label_id
         }).append("label").attr("id", function(d) {
             return "catl" + d.label_id
         }).attr("tabIndex", "0").html(function(d) {
             return d.label_name
         }).on("click", resultCategoryClick).on("focus", function(d) {
             currentObject = this;
         })
         //refresh();
 }

 function resultCategoryClick(d, i) {
     //console.log(this)
     d3.selectAll("#resultCategory div label").classed("tagSelected", false);
     d3.select(document.activeElement).classed("tagSelected", true);
     clearType();
     //d3.selectAll("#resultType").style("visibility", "hidden");
     resultTypeId = null
     resultCatId = d.label_id
     getResultType(resultCatId)
         //refresh();
 };

 function getResultType(resultCatId) {
     var url_end = totalQtr + "/" + resultCatId;
     var singleCompare = document.getElementById('singleCompare').checked
     var mode = ''
     if (singleCompare == true && secondaryStockID != null) {
         mode = 'C';
         url_end = url_end + "?stockCompare=" + secondaryStockID;
     } else {
         mode = 'S';
     }
     var url = "/type/" + primaryStockID + "/" + mode + "/" + url_end
         //var url = "/type/3266" + "/" + mode + "/" + url_end
     d3.json(url, {
         headers: {
             "Authorization": "Basic " + token
         }
     }).then(function(typeData) {
         updateResultType(typeData);
     }).catch(function(error) {
         console.log(error)
         if (error) {
             window.location.href = "/"
         }
     })
 }

 function updateResultType(typeData) {
     d3.selectAll("#resultType div label").classed("tagSelected", false);
     d3.selectAll("#resultType").style("visibility", "visible");
     //d3.selectAll("#resultType").style("visibility", "visible");
     //d3.selectAll(".options").style("visibility", "visible");
     resultTypeId = null
     d3.selectAll(".graphPanel").style("visibility", "hidden");

     var tags = d3.selectAll("#resultType").selectAll("div").data(typeData, function(d) {
         return "typdiv" + d.label_id;
     })

     tags.exit().remove()
     tags.enter().append('div').attr("class", "tag").attr("id", function(d) {
             return "typdiv" + d.label_id
         }).append("label").attr("id", function(d) {
             return "typl" + d.label_id
         }).attr("tabIndex", "0").html(function(d) {
             return d.label_name
         }).on("click", resultTypeClick)
         //refresh();
 }

 function resultTypeClick(d, i) {
     d3.selectAll("#resultType div label").classed("tagSelected", false);
     d3.select(document.activeElement).classed("tagSelected", true);
     //console.log("before " + resultTypeID);
     resultTypeId = d.label_id
         //getResultType(resultCatId)
     refresh();
 }


 var linspace = function(start, stop, num_samples) {
     var off = ((stop - start) / num_samples)
     return d3.range(0, num_samples)
         .map(function(n) {
             return Math.floor(n * off);
         });
 };

 function line_cordinates(x, y) {
     x1 = []
     y1 = []
     x2 = []
     y2 = []
     data = []
     for (i = 0; i < x.length - 1; i++) {
         data[i] = {
             x1: x[i],
             x2: x[i + 1],
             y1: y[i].price,
             y2: y[i + 1].price,
             period: y[i].period
         }
         data[x.length - 1] = {
             x1: x[x.length - 1],
             x2: x[x.length - 1],
             y1: y[x.length - 1].price,
             y2: y[x.length - 1].price,
             period: y[x.length - 1].period
         }

     }
     return data
 }

 function refresh() {
     if (primaryStockID != null && resultCatId != null && totalQtr != null && resultTypeId != null) {
         var end_url = ""
         var priceOne = ""
         var singleCompare = document.getElementById('singleCompare').checked
         var mode = ''
         if (singleCompare == true && secondaryStockID != null) {
             mode = 'C';
             end_url = "&secondaryStockID=" + secondaryStockID;
             if (getPrice2) {
                 end_url = end_url + "&price2=Y"
             }
         } else {
             mode = 'S';
         }
         var fromQtr = 102 - totalQtr;
         if (getPrice1) {
             priceOne = "&price1=Y";
         }

         var url = "/graph/" + primaryStockID + "?mode=" + mode + "&resultTypeId=" + resultTypeId + "&fromQtr=" + fromQtr + "&totalQtr=" + 20 + "&totalQtrIncome=" + totalQtr + "&categoryId=" + resultCatId + priceOne + end_url;

         d3.json(url, {
             headers: {
                 "Authorization": "Basic " + token
             }
         }).then(function(data) {
             update_svg(data);
         }).catch(function(error) {
             console.log(error)
             if (error) {
                 window.location.href = "/"
             }
         })
     }
 }

 function update_svg(data1) {

     var singleCompare = document.getElementById('singleCompare').checked
     var mode = ''
     if (singleCompare == true && secondaryStockID != null) {
         d3.selectAll("#g1").style("visibility", "visible");
         stock1 = data1.income.filter(function(d) {
             return d.name == primaryStockID;
         });
         stock2 = data1.income.filter(function(d) {
             return d.name == secondaryStockID;
         });
         st1Max = getMax(stock1);
         if (getPrice1) {
             price1Max = d3.max(data1.price1.map(function(d) {
                 return d.price;
             }));
         } else {
             price1Max = d3.max(stockPrice1.map(function(d) {
                 return d.price;
             }));
         }
         stk2Max = getMax(stock2);
         if (getPrice2) {
             price2Max = d3.max(data1.price2.map(function(d) {
                 return d.price;
             }));
         } else {
             price2Max = d3.max(stockPrice2.map(function(d) {
                 return d.price;
             }));
         }

         var dataMax = 0;
         var priceMax = 0;
         if (st1Max > stk2Max) {
             dataMax = st1Max;
         } else {
             dataMax = stk2Max;
         }
         if (price2Max > price1Max) {
             priceMax = price2Max;
         } else {
             priceMax = price1Max;
         }
         var name = d3.select("#companyLabel").html();
         render(graphOne, stock1, name, getPrice1 ? data1.price1.slice(data1.price1.length - (totalQtr * 3)) : stockPrice1.slice(stockPrice1.length - (totalQtr * 3)), null, dataMax, priceMax);
         if (getPrice1) {
             stockPrice1 = data1.price1;
         }
         getPrice1 = false;
         d3.selectAll("#g2").style("visibility", "visible");
         name = d3.select("#compareLabel").html();
         render(graphTow, stock2, name, null, getPrice2 ? data1.price2.slice(data1.price2.length - (totalQtr * 3)) : stockPrice2.slice(stockPrice2.length - (totalQtr * 3)), dataMax, priceMax);
         if (getPrice2) {
             stockPrice2 = data1.price2;
         }
         getPrice2 = false;

     } else {
         d3.selectAll("#g1").style("visibility", "visible");
         var dataMax = 0;
         if (getPrice1) {
             priceMax = d3.max(data1.price1.map(function(d) {
                 return d.price;
             }));
         } else {
             priceMax = d3.max(stockPrice1.map(function(d) {
                 return d.price;
             }));
         }
         dataMax = getMax(data1.income);
         var name = d3.select("#companyLabel").html();
         render(graphOne, data1.income, name, getPrice1 ? data1.price1.slice(data1.price1.length - (totalQtr * 3)) : stockPrice1.slice(stockPrice1.length - (totalQtr * 3)), null, dataMax, priceMax);
         if (getPrice1) {
             stockPrice1 = data1.price1;
         }
         getPrice1 = false;
     }
 }

 function render_price(svg, width, height, seperation_distance, price, priceMax) {
     x = linspace(seperation_distance, width, price.length)
         //var n = price.length;
     data = line_cordinates(x, price);
     var width_offset = Math.floor((width - ((totalQtr) * seperation_distance)) / totalQtr);
     width_offset = Math.min(width_offset, 30);
     var xScale = d3.scaleLinear()
         .domain([0, d3.max(x)]) // input
         .range([0, (width_offset * totalQtr - 1) + (totalQtr * seperation_distance)]); // output
     var yScale = d3.scaleLinear().domain([0, priceMax]).range([height, 0]);
     var line = d3.line()
         .x(function(d, i) {
             return xScale(Math.floor(d.x1));
         })
         .y(function(d) {
             //console.log("for y i: " + i + ", d:" + Math.floor(yScale(d.y1)));
             return Math.floor(yScale(d.y1));
         }).curve(d3.curveBasis);
     svg.selectAll("path").remove();
     //var lines = timelineChart();
     //svg.datum(data.map(d => d.y1)).call(lines).attr("stroke", "black").attr("stroke-width", "2px").attr("fill", "none");;
     svg.append("path").transition().duration(1500).attr("d", line(data)).attr("stroke", "black").attr("stroke-width", "2px").attr("fill", "none");
     /*
      svg.selectAll("circle").remove();
                 var bind = svg.selectAll("circle").data(data, function(d) {
                     return d.period;
                 });
                 bind.enter().append("circle").attr("cx", function(d, i) {
                     return xScale(Math.floor(d.x1))
                 }).attr("cy", function(d, i) {
                     return Math.floor(yScale(d.y1))
                 }).attr("r", "3").attr("fill", "black").style("cursor", "pointer").on("mouseover", function(d, i) {
                     var x = d3.select(this).attr("cx");
                     var y = d3.select(this).attr("cy");
                     svg.append("text").attr("id", "price").attr("x", x).attr("y", y).style("z-index", "9").attr("stroke", "blue").attr("stroke-width", "1px").html(d.y1);
                 }).on("mouseout", function(d, i) {
                     svg.select("#price").remove();
                 });
     */
     svg.select("#rAxis").remove();
     svg.append("g").attr("id", "rAxis").call(d3.axisLeft(yScale).tickFormat(function(d, i) {
         return d + " Rs";
     })).attr("transform", "translate(" + width + ",0)");
 }

 function render(svg, data, name, price1, price2, dataMax, priceMax) {
     var duration = 2000;
     var delay = 100;
     var seperation_distance = 20;
     var width = Math.floor(svg1Width - margin.left - margin.right);
     var height = Math.floor(svg1Height - margin.top - margin.bottom);
     var scaleData = d3.scaleLinear().domain([0, dataMax]).range([0, height]);
     var width_offset = Math.floor((width - ((data.length) * seperation_distance)) / data.length);
     width_offset = Math.min(width_offset, 30);
     var multiplier = Math.floor(width / Object.keys(data).length);
     svg.select("text").remove();
     svg.append("text").attr("y", 10).attr("x", width / 2).style("text-anchor", "middle").html(name).attr("transform", "translate(0,-" + margin.top + ")");
     rectangles = svg.selectAll('rect').data(data, function(d, i, n) {
         return d.name;
     });

     rectangles.exit().remove();
     rectangles.enter().append("rect").merge(rectangles).attr("width", width_offset).style("fill", "lightgreen").attr("y", function(d, i) {
         return height - 5 - scaleData(d.value);
     }).transition().delay(function(d, i) {
         return i * 30;
     }).duration(duration).attr("height", function(d) {
         return scaleData(Math.max(d.value, 0));
     }).attr("x", function(d, i) {
         return (i * width_offset) + ((i + 1) * seperation_distance);
     }).ease(d3.easeElastic);

     svg.select("#yaxis").remove();
     svg.append("g").attr("id", "yaxis").call(d3.axisRight(scaleData).tickFormat(function(d) {
         if ((resultCatId == 1 && resultTypeId == 1) || (resultCatId == 11) || (resultCatId == 12)) {
             return Math.floor(dataMax - d) / 100 + " Cr";
         } else {
             return Math.floor(dataMax - d);
         }
     })).attr("transform", "translate(-" + margin.left + ",0)");

     var tickV = []
     for (i = 0; i < data.length; i++) {
         tickV[i] = (i * width_offset) + ((i + 1) * seperation_distance) + (width_offset / 2);
     }

     var xscale = d3.scaleOrdinal(data.length).domain(getNames(data)).range(tickV);
     svg.select("#xaxis").remove();
     svg.append("g").attr("id", "xaxis").call(d3.axisTop(xscale).tickFormat(function(d, i) {
         return data[i].year;
     })).attr("transform", "translate(0," + height + ")");

     if (price1 != null) {
         render_price(svg, width, height, seperation_distance, price1, priceMax);
     }
     if (price2 != null) {
         render_price(svg, width, height, seperation_distance, price2, priceMax);
     }
 }

 function clearCategory() {
     d3.selectAll("#resultCategory div").remove();
     d3.selectAll("#resultCategory").style("visibility", "hidden");
 }

 function clearType() {
     d3.selectAll("#resultType div").remove();
     d3.selectAll("#resultType").style("visibility", "hidden");
 }

 function resetOptions() {
     d3.selectAll("#noOfQtr label").style("background", "");
     //d3.selectAll("#singleCompare").property("unchecked");
     d3.selectAll(".qy input[type=checkbox]").property("checked", false);
     d3.selectAll(".cinput .enabled").attr("class", "disabled");
     totalQtr = 20;
 }

 function hideGraphPanel() {
     d3.selectAll(".graphPanel").style("visibility", "hidden");
 }

 window.onclick = function(event) {
     if (!event.target.matches('.dropdown-items')) {
         clearSearchResults('#mainSearchResults');
     }
 }
 window.addEventListener('keyup', function(e) {
     if (e.key === "Enter") {
         var cur = d3.select(document.activeElement)
         var f = cur.on("click")
         if (typeof f === "undefined") {
             //this is for javacript events
             document.activeElement.click()
         } else {
             //this is for d3 events
             f(cur.property("__data__"), 0)
         }
     }

     if (e.key === "Tab") {
         //document.activeElement.click();
     }


     if (e.key === "ArrowDown") {
         try {
             var parentID = d3.select(document.activeElement).property("parentElement").id;
             var parentEle = d3.select("#" + parentID).property("parentElement").id
             var cat = d3.select("#" + parentEle + " + div :first-child :first-child")
             if (cat != null) {
                 document.getElementById(cat.attr("id")).focus()
             }
         } catch (e) {

         }
     }
     if (e.key === "ArrowUp") {
         try {
             var parentID = d3.select(d3.select(document.activeElement).property("parentElement")).property("parentElement").id;
             if (parentID === "resultType") {
                 var cat = d3.select("#resultCategory :first-child :first-child")
                 if (cat != null) {
                     document.getElementById(cat.attr("id")).focus()
                 }
             }
         } catch (e) {

         }
     }
     if (e.key === "Escape") {
         document.activeElement.blur()
         document.getElementById("companyName").focus()
     }
 });