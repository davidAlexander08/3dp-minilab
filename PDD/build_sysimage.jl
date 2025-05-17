using PackageCompiler

create_sysimage(
    [:PDD],
    sysimage_path = "PDDApp.dll",
    precompile_execution_file = "PDD/precompile.jl",
    project = "PDD"
)


#create_sysimage(
#    [:PDDApp],
#    sysimage_path = "PDDAppSysimage.dll",
#    precompile_execution_file = "PDDApp/precompile.jl",
#    project = "PDDApp"
#)