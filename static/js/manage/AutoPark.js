
;(function( $ ){

	$.fn.AutoPark = function( options ) {
		var Setting = $.extend( {
			LINE:		'#line', 
			PARK:			'#park'
			
		}, options);
		
		return this.each(function() {
			var jsonFile;
	    	var dataUrl = "autopark";
		
			$(function() {
				initialize();
			});
			
			function initialize(){
				$.ajax({
					type: "GET",
					url: dataUrl,
					success: function(data) {
						jsonFile = $(data);
						parseFile = JSON.parse(JSON.stringify(jsonFile[0]));
						rights = JSON.parse(JSON.stringify(jsonFile[1]));
						console.log('rights  '+rights)		
						_loadLine();
						addEventList();
					},
					error: function() {
						console.log("Failed to get json");
					}
				});  
			}
			function _loadLine(){
				var listline = [];
			  for(var j = 0; j<rights.length;j++){
				  code = rights[j];
				for (var i = 0; i < parseFile.length; i++){
					if(code == parseFile[i][2]){
					 listline.push(parseFile[i][1]);
					}
				}
			   }
			   if(listline.length>1){
				listline.push("ทั้งหมด")
			   }
                const setLine = new Set(listline);
				let arrayLine= Array.from(setLine);
				
				AddToView(arrayLine,Setting.LINE);
			}
			

			function _loadPark(line)
			{
				var listpark = [];
				$(Setting.PARK).empty();
				for(var j = 0; j<rights.length;j++){
					code = rights[j];
					for (var i = 0; i < parseFile.length; i++){
						if(code == parseFile[i][2]){
							if(parseFile[i][1] == line){
							listpark.push(parseFile[i][0])
							}
						}
					}
				}
				if(listpark.length>1 || line=="ทั้งหมด"){
					listpark.push("ทั้งหมด")
				}

				console.log('listpark'+listpark)

				AddToView(listpark,Setting.PARK);
			}
			
			
			
			function addEventList(){
				
				$(Setting.LINE).change(function(e) {
					var selected_p = $(this).val();
				
			    	_loadPark(selected_p);
					
				
				});
			
			}

			function AddToView(list,key){
				for (var i = 0;i<list.length;i++) {
					$(key).append("<option value='"+list[i]+"'>"+list[i]+"</option>");	
					
				}	
					
			}
			
			
		});
	};
})( jQuery );
