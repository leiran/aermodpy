if __name__ == "__main__":
    
    from aermodpy.aermod import *
    from aermodpy.color_dicts import color_dicts
    
    directory = "."
    buildings=True
    
    #building_fn = "SUNYESF_RSG_Modified.PIP"
    #directory = "../modeling output"
    building_fn = "SUNYESF_final.PIP"
    filename  = "SUNYESF_1HR_NO2.GRF"
    vars = "grf"
    c_vars = "1h-no2"
    pollutant = "NO2"
    background = 49.6 #ppb
    
    # options
    options = {"colorslevels" : color_dicts[c_vars]
              #,"colorbar_spacing" : "uniform"
              #,"interpolation_method" : "nearest"
              #,"contours" : 0.05
              ,"interpolation_method" : "cubic"
              ,"scalar" : 0.53163211057948 #inverse of 1.881
              ,"pollutant" : pollutant
              
              # receptor options
              ,"receptor_size" : 0.05
              ,"receptor_type" : "."
              ,"exclude_flagpole_receptors" : True
              
              # max conc options
              ,"max_plot" : 30
              ,"max_textsize" : 8
              
              # plot options
              ,"distance_from_origin" : 500
              ,"tickinterval" : 100
              #,"noticks" : True
              ,"labelsize" : 8
              #,"labelgap" : 8
              #,"nocolorbar" : True
              ,"scale_decimals" : "%1.1f"
              ,"sources" : 8
              ,"buildings" : True
              ,"title_size" : 10
              }
    
    p = post(filename
            ,directory=directory
            ,vars_index=vars_indices[vars]
            ,verbose=True
            ,DEBUG=True
            )
    print("--> successful file import:", filename)
    
    # process file
    p.processPOSTData()
    
    # add buildings
    if buildings:
        p.add_buildings(building_fn
                       ,directory=directory
                       )
    
        # make plotfile for one hour
        print("Preparing plots...")
        for r_type, r_form, source_group in p.datatypes:
            for slice in range(p.POSTdata[(r_type, r_form, source_group)].shape[1]):
                # p.gridplot(r_type     # which datatype?
                          # ,r_form     # what's the form of the data??
                          # ,source_group      # source group
                          # ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+".png"
                          # ,**options
                          # )
                p.gridplot(r_type     # which datatype?
                          ,r_form     # what's the form of the data??
                          ,source_group      # source group
                          ,add_background=background
                          ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+"_withbg.png"
                          ,**options
                          )
                # p.printdata(r_type     # which datatype?
                           # ,r_form     # what's the form of the data??
                           # ,source_group      # source group
                           # ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+".txt"
                           # ,**options
                           # )
    
        options["exclude_flagpole_receptors"] = False
        options["distance_from_origin"] = 200
        options["tickinterval"] = 50
        options["interpolation_method"] = "nearest"
        
        # for r_type, r_form, source_group in p.datatypes:
            # for slice in range(p.POSTdata[(r_type, r_form, source_group)].shape[1]):
                # p.gridplot(r_type     # which datatype?
                          # ,r_form     # what's the form of the data??
                          # ,source_group      # source group
                          # ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+"_flagpoles.png"
                          # ,**options
                          # )
                # p.gridplot(r_type     # which datatype?
                          # ,r_form     # what's the form of the data??
                          # ,source_group      # source group
                          # ,add_background=background
                          # ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+"_withbg_flagpoles.png"
                          # ,**options
                          # )
                # p.printdata(r_type     # which datatype?
                           # ,r_form     # what's the form of the data??
                           # ,source_group      # source group
                           # ,filename="out/SUNYESF_"+pollutant+"_"+("_".join([r_type, r_form, source_group])).replace(" ", "_")+"_flagpoles.txt"
                           # ,**options
                           # )
    
    
    print("--> plot(s) creation successful")
