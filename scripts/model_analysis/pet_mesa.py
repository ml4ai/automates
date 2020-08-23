from automates.model_analysis.mesa import mesa


def main():
    pno_str = "((TMAX+273.)**4+(TMIN+273.)**4) / 2.0"
    asce_str = "(TMAX + TMIN) / 2.0"

    (aligned_pno, aligned_asce, var_map) = mesa(pno_str, asce_str)
    print(aligned_pno)
    print(aligned_asce)


if __name__ == "__main__":
    main()
