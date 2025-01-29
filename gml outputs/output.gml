<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<imaer:FeatureCollectionCalculator xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:imaer="http://imaer.aerius.nl/6.0"
    xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="NL.IMAER.Collection"
    xsi:schemaLocation="http://imaer.aerius.nl/6.0 https://imaer.aerius.nl/6.0/IMAER.xsd">
    <imaer:metadata>
        <imaer:AeriusCalculatorMetadata>
            <imaer:project>
                <imaer:ProjectMetadata>
                    <imaer:year>2025</imaer:year>
                </imaer:ProjectMetadata>
            </imaer:project>
            <imaer:situation>
                <imaer:SituationMetadata>
                    <imaer:name>Bridge Reconstruction Over River</imaer:name>
                    <imaer:reference>Rxa7Z4h3L1Cx</imaer:reference>
                    <imaer:situationType>PROPOSED</imaer:situationType>
                </imaer:SituationMetadata>
            </imaer:situation>
            <imaer:version>
                <imaer:VersionMetadata>
                    <imaer:aeriusVersion>2024.0.1_20241009_75e59949f9</imaer:aeriusVersion>
                    <imaer:databaseVersion>2024_75e59949f9_calculator_nl_stable</imaer:databaseVersion>
                </imaer:VersionMetadata>
            </imaer:version>
        </imaer:AeriusCalculatorMetadata>
    </imaer:metadata>
    <imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.1">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.1</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Demolition Excavator</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.1.POINT">
                        <gml:pos>138230.11889922134 474050.24587658900</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>10.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>25.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>8.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>12.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="ZUT">
        <imaer:description>Excavator used for demolishing old bridge structure.</imaer:description>
        <imaer:operatingHoursPerYear>1100</imaer:operatingHoursPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.2">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.2</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Crane</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.2.POINT">
                        <gml:pos>138231.11913450734 474052.24784565842</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>5.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>20.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>7.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>10.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="B4T">
        <imaer:description>Crane used for lifting bridge debris.</imaer:description>
        <imaer:literFuelPerYear>1200</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.3">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.3</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Concrete Pump</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.3.POINT">
                        <gml:pos>138232.11976543312 474054.24934219023</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>7.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>28.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>6.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>11.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="B2T">
        <imaer:description>Concrete pump for placing concrete in bridge construction.</imaer:description>
        <imaer:literFuelPerYear>1300</imaer:literFuelPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:OffRoadMobileSourceEmissionSource sectorId="3210" gml:id="ES.4">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>ES.4</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:label>Masonry Lifting Crane</imaer:label>
        <imaer:geometry>
            <imaer:EmissionSourceGeometry>
                <imaer:GM_Point>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="ES.4.POINT">
                        <gml:pos>138233.12045637455 474056.25100256873</gml:pos>
                    </gml:Point>
                </imaer:GM_Point>
            </imaer:EmissionSourceGeometry>
        </imaer:geometry>
        <imaer:emission>
            <imaer:Emission substance="NH3">
                <imaer:value>6.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NOX">
                <imaer:value>30.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="PM10">
                <imaer:value>5.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:emission>
            <imaer:Emission substance="NO2">
                <imaer:value>9.0</imaer:value>
            </imaer:Emission>
        </imaer:emission>
        <imaer:offRoadMobileSource>
    <imaer:StandardOffRoadMobileSource offRoadMobileSourceType="MUT">
        <imaer:description>Crane used for lifting masonry blocks during bridge construction.</imaer:description>
        <imaer:operatingHoursPerYear>1400</imaer:operatingHoursPerYear>
    </imaer:StandardOffRoadMobileSource>
</imaer:offRoadMobileSource>
        </imaer:OffRoadMobileSourceEmissionSource>
</imaer:featureMember><imaer:featureMember>
    <imaer:CalculationPoint gml:id="CP.1">
        <imaer:identifier>
            <imaer:NEN3610ID>
                <imaer:namespace>NL.IMAER</imaer:namespace>
                <imaer:localId>CP.1</imaer:localId>
            </imaer:NEN3610ID>
        </imaer:identifier>
        <imaer:GM_Point>
            <gml:Point srsName="urn:ogc:def:crs:EPSG::28992" gml:id="CP.1.POINT">
                <gml:pos>136707.0 475063.0</gml:pos>
            </gml:Point>
        </imaer:GM_Point>
        <imaer:label>Oostelijke Vechtplassen (2 km)</imaer:label>
    </imaer:CalculationPoint>
</imaer:featureMember>
</imaer:FeatureCollectionCalculator>  