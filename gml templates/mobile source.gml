<imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="{sectorid}" gml:id="ES.{q}">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.{q}</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>{label}</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.{q}.POINT">
                        <gml:pos>{position}</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>{NH3}</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>{NOX}</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>{PM10}</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>{NO2}</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        {specficimobilesource}
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember>