// Copyright (c) 2026, logeshwar and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Expense Claim", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Expense Claim', {
	setup(frm){
	    frm.set_query("budget",function(){
	        const today=new Date();
	        const month=today.getMonth()+1;
	        const year=today.getFullYear();
	        let quarter;
	        if(month<=3){
	            quarter="Q1";
	        }
	        else if(month<=6){
	            quarter="Q2";
	        }
	        else if(month<=9){
	            quarter="Q3";
	        }
	        else{
	            quarter="Q4";
	        }
	        return{
	            filters:{
	                department:frm.doc.department,
	                fiscal_year:year,
	                fiscal_quarter:quarter
	            }
	        }
	    })
	}
})

frappe.ui.form.on('Expense Claim', {
	refresh(frm) {
		if(frm.doc.status){
		    let color="gray";
		    if(frm.doc.status=="Approved"){
		        color="green";
		    }
		    else if(frm.doc.status=="Pending Approval"){
		        color="yellow";
		    }
		    else if(frm.doc.status=="Rejected"){
		        color="orange";
		    }
		    else if(frm.doc.status=="Cancelled"){
		        color="red";
		    }
		    else if(frm.doc.status=="Reimbursed"){
		        color="blue";
		    }
		    
		    frm.dashboard.add_indicator(frm.doc.status,color);
		}
		
		if(frm.doc.status=="Pending Approval" && (frappe.user.has_role("SG Department Head")||frappe.user.has_role("SG Finance Manager"))){
		    frm.add_custom_button("Approve",function(){
		        frm.set_value("status","Approved");
		        frm.save();
		    })
		}
		
		if(frm.doc.budget){
		    frappe.call({
		        method:"spendgate.api.budget_status",
		        args:{budget_name:frm.doc.budget},
		        callback:function(r){
		            if(r.message){
		                const data=r.message;
		                let rem_color;
                		if(data.remaining>0){
                		    rem_color="green";
                		}
                		else{
                		    rem_color="red";
                		}
		                frm.budget_remaining=data.remaining;
		                frm.dashboard.add_indicator(`Budget Remaining: ${data.remaining}`,rem_color)
		            }
		        }
		    })
		}

        if(frappe.user.has_role("SG Department Head")||frappe.user.has_role("SG Finance Manager")){
    		frm.add_custom_button("Reject Claim",function(){
    		    let dialog=new frappe.ui.Dialog({
    		        title:"Reject Claim",
    		        fields:[{
    		            label:"Rejection reason",
    		            fieldname:"rejection_reason",
    		            fieldtype:"Small Text",
    		            reqd:1
    		        }],
    		        primary_action_label:"Reject",
    		        primary_action(values){
    		            console.log("Rejection reason:",values.rejection_reason);
    		            frm.set_value("status", "Rejected");
    		            frm.save();
    		            dialog.hide();
    		        }
    		    })
    		    dialog.show();
    		});
	    }
		
		frm.add_custom_button("Reassign Department",function(){
		    frappe.prompt(
		        [{
		            label:"Department",
		            fieldname:"department",
		            fieldtype:"Link",
		            options:"Department",
		            reqd:1
		        }],
		        function(values){
		            frappe.confirm(
		                `Confirm to change the department`,
		                function(){
		                    frappe.call({
		                        method:"spendgate.api.reassign_department",
		                        args: {
                                    claim_name: frm.doc.name,
                                    department: values.department
                                },
                                callback: function(r) {
                                    console.log("Department reassigned");
                                    frm.set_value("department", values.department);
                                    frm.trigger("department");
                                }
		                    })
		                },
		                function(){
		                    console.log("user rejected");
		                }
		            )
		        },
		        "Reassign Department",
		        "Next"
		    )
		})
	}
})

frappe.ui.form.on('Expense Line', {
	amount(frm,cdt,cdn) {
		let total=0;
		for(let row of frm.doc.expense_lines){
		    total+=row.amount;
		}
		frappe.model.set_value(frm.doctype,frm.docname,"total_amount",total);
		
		if(total>frm.budget_remaining){
		    frappe.show_alert({
		        message:`Budget remaining: ${frm.budget_remaining} | Total exceeds the remaining budget`,
		        indicator:"red"
		    })
		}
	}
})

frappe.ui.form.on('Expense Claim',{
    budget(frm){
        if(frm.doc.budget){
            frappe.call({
                method:"spendgate.api.budget_status",
                args:{budget_name:frm.doc.budget},
                callback:function(r){
                    if(r.message){
                        frm.budget_remaining=r.message.remaining;
                    }
                }
            })
        }
    }
})