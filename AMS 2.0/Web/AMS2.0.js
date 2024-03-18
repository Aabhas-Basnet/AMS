function Add_record(){
	    Name = document.getElementById("fname").value;
	    Id = document.getElementById("uid").value;
	    Fac = document.getElementById("faculty").value;
	    Batch = document.getElementById("Batch").value;
		
		if (Name && Id && Fac && Batch != null){
		   eel.Add_record(Id,Name,Fac,Batch);
		}
	}
	
	function Del_record(){
		Password = window.prompt("ENTER PIN TO DELETE RECORD");
	    Id = document.getElementById("uid1").value;
		
		if (Id != null){
		   eel.Del_record(Id,Password);
		}
	}
	
	function Add_attendance(){
		eel.Attendance();
	}
	
  function Add_Leave(){
	    Id = document.getElementById("uid2").value;
		
		startDate = document.getElementById("from_dates").value;;
		endDate = document.getElementById("to_dates").value;
		Dates = [startDate];
		
		if (startDate && endDate != ''){
		  Dates = getDates(startDate, endDate);
		}		
		
		if ((Id && Dates != null)  && Dates[0] != ''){
		   eel.Add_Leave(Id,Dates);
		}
		
	}
	
	function Generate_record(){
		Fac = document.getElementById("faculty2").value;
	    Batch = document.getElementById("Batch2").value;
		
		startDate = document.getElementById("from_dates1").value;;
		endDate = document.getElementById("to_dates1").value;
		Dates = [startDate];
		
		if (startDate && endDate != ''){
		  console.log('T')
		  Dates = getDates(startDate, endDate);
		}	
		
		if ((Fac && Batch != null) && Dates[0] != ''){
		   eel.Generate_attendance(Dates,Fac,Batch);
		}
	}
	
  function getDates(startDate, endDate) {
   const dates = [];
   let currentDate = new Date(startDate);
   
   while (currentDate <= new Date(endDate)) {
    dates.push(currentDate.toISOString().substr(0, 10));
    currentDate.setDate(currentDate.getDate() + 1);
  }
    return dates;
  }	